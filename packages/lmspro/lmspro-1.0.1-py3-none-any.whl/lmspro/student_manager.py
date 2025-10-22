
from pathlib import Path
from data_manager import DataManager


class StudentManager:
    """
    Manage student records using DataManager for file operations.

    ✅ Add, remove, list students
    ✅ Stores data safely in JSON
    ✅ Automatically saves and loads from file
    """

    def __init__(self, data_file="data/students.json"):
        # Composition: use DataManager inside StudentManager
        self.dm = DataManager(data_file)
        self.students = self.dm.read_json() or {}  # load existing data if any

    # -----------------------------
    # ➕ Add Student
    # -----------------------------
    def add_student(self, student_id: str, name: str, course: str):
        """Add a new student."""
        if student_id in self.students:
            print(f"⚠️ Student ID {student_id} already exists.")
            return
        self.students[student_id] = {"name": name, "course": course}
        self._save()
        print(f"✅ Added student: {name}")

    # -----------------------------
    # 🗑️ Remove Student
    # -----------------------------
    def remove_student(self, student_id: str):
        """Remove a student by ID."""
        if student_id not in self.students:
            print(f"⚠️ Student ID {student_id} not found.")
            return
        removed = self.students.pop(student_id)
        self._save()
        print(f"🗑️ Removed student: {removed['name']}")

    # -----------------------------
    # 📋 List Students
    # -----------------------------
    def list_students(self):
        """Display all students."""
        if not self.students:
            print("📭 No students found.")
            return
        print("\n📚 Current Students:")
        for sid, info in self.students.items():
            print(f"  • ID: {sid} | Name: {info['name']} | Course: {info['course']}")

    # -----------------------------
    # 🔍 Search Student
    # -----------------------------
    def find_student(self, student_id: str):
        """Find and display a student by ID."""
        student = self.students.get(student_id)
        if student:
            print(f"👤 Found: {student['name']} ({student['course']})")
            return student
        print(f"⚠️ Student ID {student_id} not found.")
        return None

    # -----------------------------
    # 💾 Save Helper
    # -----------------------------
    def _save(self):
        """Save current data to file."""
        self.dm.write_json(self.students)
