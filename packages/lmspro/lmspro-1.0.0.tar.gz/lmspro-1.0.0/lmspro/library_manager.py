from data_manager import DataManager
from input_helper import get_str, get_int, confirm
from datetime import datetime, timedelta
from colorama import Fore

class LibraryManager:
    """
    Manage library books, borrow/return, copies, and fines.
    Data stored via DataManager (JSON):
    - books.json: {book_id: {"title":..., "author":..., "copies": int}}
    - borrow.json: {book_id: [{"student_id":..., "borrow_date":..., "due_date":..., "returned": bool}]}
    """

    FINE_PER_DAY = 5  # currency units per day late

    def __init__(self, books_file="data/books.json", borrow_file="data/borrow.json"):
        self.dm_books = DataManager(books_file)
        self.dm_borrow = DataManager(borrow_file)
        self.books = self.dm_books.read_json() or {}
        self.borrow_history = self.dm_borrow.read_json() or {}

    # -----------------------------
    # ➕ Add Book
    # -----------------------------
    def add_book(self, book_id: str, title: str, author: str, copies: int = 1):
        if book_id in self.books:
            self.books[book_id]["copies"] += copies
            print(Fore.GREEN + f"✅ Added {copies} more copies of {title}. Total copies: {self.books[book_id]['copies']}")
        else:
            self.books[book_id] = {"title": title, "author": author, "copies": copies}
            print(Fore.GREEN + f"✅ Added new book: {title} by {author} ({copies} copies)")
        self._save_books()

    # -----------------------------
    # 🗑 Remove Book
    # -----------------------------
    def remove_book(self, book_id: str):
        if book_id not in self.books:
            print(Fore.RED + f"⚠️ Book ID {book_id} not found.")
            return
        if confirm(f"Are you sure you want to remove '{self.books[book_id]['title']}'? (y/n): "):
            removed = self.books.pop(book_id)
            self._save_books()
            print(Fore.GREEN + f"🗑️ Removed book: {removed['title']}")
        else:
            print(Fore.YELLOW + "❌ Action cancelled.")

    # -----------------------------
    # 📋 List Books
    # -----------------------------
    def list_books(self):
        if not self.books:
            print(Fore.YELLOW + "📭 No books available.")
            return
        print(Fore.MAGENTA + "\n📚 Library Books:")
        for bid, info in self.books.items():
            available = self.get_available_copies(bid)
            print(f" • ID: {bid} | {info['title']} by {info['author']} | Copies: {info['copies']} | Available: {available}")

    # -----------------------------
    # 🔄 Borrow Book
    # -----------------------------
    def borrow_book(self, book_id: str, student_id: str, days: int = 14):
        if book_id not in self.books:
            print(Fore.RED + f"⚠️ Book ID {book_id} not found.")
            return

        available = self.get_available_copies(book_id)
        if available <= 0:
            print(Fore.YELLOW + f"⚠️ No available copies for '{self.books[book_id]['title']}'")
            return

        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=days)

        entry = {
            "student_id": student_id,
            "borrow_date": borrow_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "returned": False
        }

        if book_id not in self.borrow_history:
            self.borrow_history[book_id] = []
        self.borrow_history[book_id].append(entry)
        self._save_borrow()
        print(Fore.GREEN + f"✅ {student_id} borrowed '{self.books[book_id]['title']}' until {due_date.date()}")

    # -----------------------------
    # 🔙 Return Book
    # -----------------------------
    def return_book(self, book_id: str, student_id: str):
        if book_id not in self.borrow_history:
            print(Fore.RED + f"⚠️ No borrow record found for Book ID {book_id}")
            return

        for entry in self.borrow_history[book_id]:
            if entry["student_id"] == student_id and not entry["returned"]:
                entry["returned"] = True
                self._save_borrow()

                due_date = datetime.strptime(entry["due_date"], "%Y-%m-%d")
                return_date = datetime.now()
                late_days = (return_date - due_date).days
                fine = self.FINE_PER_DAY * late_days if late_days > 0 else 0

                if fine > 0:
                    print(Fore.RED + f"⚠️ Book returned late by {late_days} days. Fine: {fine}")
                else:
                    print(Fore.GREEN + "✅ Book returned on time. No fine.")
                return

        print(Fore.YELLOW + f"⚠️ No active borrow found for student {student_id} and book {book_id}")

    # -----------------------------
    # 📊 Available Copies
    # -----------------------------
    def get_available_copies(self, book_id: str):
        total_copies = self.books[book_id]["copies"]
        borrowed = sum(1 for b in self.borrow_history.get(book_id, []) if not b["returned"])
        return total_copies - borrowed

    # -----------------------------
    # 💾 Save Helpers
    # -----------------------------
    def _save_books(self):
        self.dm_books.write_json(self.books)

    def _save_borrow(self):
        self.dm_borrow.write_json(self.borrow_history)
