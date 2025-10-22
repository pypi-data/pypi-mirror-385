from student_manager import StudentManager
from course_manager import CourseManager
from enrollment_manager import EnrollmentManager
from library_manager import LibraryManager
from report_manager import ReportManager
from input_helper import get_choice, get_str, get_int, confirm
from colorama import Fore, Style

def main_menu():
    # Initialize all managers
    sm = StudentManager()
    cm = CourseManager()
    em = EnrollmentManager()
    lm = LibraryManager()
    rm = ReportManager()

    while True:
        print("\n" + "="*50)
        print(Fore.MAGENTA + "🎓 FULL LMS MANAGEMENT SYSTEM")
        print("="*50)

        choice = get_choice(
            "Select module:",
            ["Students", "Courses", "Enrollments", "Library", "Reports", "Exit"]
        )

        # -----------------------------
        # STUDENTS MODULE
        # -----------------------------
        if choice == "Students":
            student_menu(sm)

        # -----------------------------
        # COURSES MODULE
        # -----------------------------
        elif choice == "Courses":
            course_menu(cm)

        # -----------------------------
        # ENROLLMENTS MODULE
        # -----------------------------
        elif choice == "Enrollments":
            enrollment_menu(em, sm, cm)

        # -----------------------------
        # LIBRARY MODULE
        # -----------------------------
        elif choice == "Library":
            library_menu(lm, sm)

        # -----------------------------
        # REPORTS MODULE
        # -----------------------------
        elif choice == "Reports":
            reports_menu(rm, sm, cm, em, lm)

        # -----------------------------
        # EXIT
        # -----------------------------
        elif choice == "Exit":
            if confirm("Do you really want to exit? (y/n): "):
                print(Fore.GREEN + "👋 Goodbye!")
                break

# -----------------------------
# STUDENT MENU
# -----------------------------
def student_menu(sm):
    while True:
        choice = get_choice(
            "Student Menu:",
            ["Add Student", "Remove Student", "List Students", "Back"]
        )

        if choice == "Add Student":
            sid = get_str("Enter student ID: ").upper()
            name = get_str("Enter student name: ", capitalize=True)
            course = get_str("Enter course: ", capitalize=True)
            sm.add_student(sid, name, course)
        elif choice == "Remove Student":
            sid = get_str("Enter student ID to remove: ").upper()
            sm.remove_student(sid)
        elif choice == "List Students":
            sm.list_students()
        else:
            break

# -----------------------------
# COURSE MENU
# -----------------------------
def course_menu(cm):
    while True:
        choice = get_choice(
            "Course Menu:",
            ["Add Course", "Remove Course", "List Courses", "Back"]
        )

        if choice == "Add Course":
            cid = get_str("Enter course ID: ").upper()
            name = get_str("Enter course name: ", capitalize=True)
            desc = get_str("Enter course description: ")
            cm.add_course(cid, name, desc)
        elif choice == "Remove Course":
            cid = get_str("Enter course ID to remove: ").upper()
            cm.remove_course(cid)
        elif choice == "List Courses":
            cm.list_courses()
        else:
            break

# -----------------------------
# ENROLLMENT MENU
# -----------------------------
def enrollment_menu(em, sm, cm):
    while True:
        choice = get_choice(
            "Enrollment Menu:",
            ["Enroll Student", "Unenroll Student", "List Enrollments", "Back"]
        )

        if choice == "Enroll Student":
            sid = get_str("Enter student ID: ").upper()
            cid = get_str("Enter course ID: ").upper()
            if sm.students.get(sid) and cm.courses.get(cid):
                em.enroll(sid, cid)
            else:
                print(Fore.RED + "⚠️ Invalid student or course ID.")
        elif choice == "Unenroll Student":
            sid = get_str("Enter student ID: ").upper()
            cid = get_str("Enter course ID: ").upper()
            em.unenroll(sid, cid)
        elif choice == "List Enrollments":
            em.list_enrollments()
        else:
            break

# -----------------------------
# LIBRARY MENU
# -----------------------------
def library_menu(lm, sm):
    while True:
        choice = get_choice(
            "Library Menu:",
            ["Add Book", "Remove Book", "List Books", "Borrow Book", "Return Book", "Back"]
        )

        if choice == "Add Book":
            bid = get_str("Enter book ID: ").upper()
            title = get_str("Enter title: ", capitalize=True)
            author = get_str("Enter author: ", capitalize=True)
            copies = get_int("Enter number of copies:", 1, 1000)
            lm.add_book(bid, title, author, copies)

        elif choice == "Remove Book":
            bid = get_str("Enter book ID to remove: ").upper()
            lm.remove_book(bid)

        elif choice == "List Books":
            lm.list_books()

        elif choice == "Borrow Book":
            bid = get_str("Enter book ID to borrow: ").upper()
            sid = get_str("Enter student ID: ").upper()
            if sid in sm.students:
                lm.borrow_book(bid, sid)
            else:
                print(Fore.RED + "⚠️ Student not found.")

        elif choice == "Return Book":
            bid = get_str("Enter book ID to return: ").upper()
            sid = get_str("Enter student ID: ").upper()
            lm.return_book(bid, sid)
        else:
            break

# -----------------------------
# REPORTS MENU
# -----------------------------
def reports_menu(rm, sm, cm, em, lm):
    while True:
        choice = get_choice(
            "Reports Menu:",
            ["Students CSV/PDF", "Courses CSV/PDF", "Enrollments CSV/PDF", "Library CSV/PDF", "Back"]
        )

        if choice == "Students CSV/PDF":
            data = [{"ID": k, "Name": v["name"], "Course": v["course"]} for k, v in sm.students.items()]
            headers = ["ID", "Name", "Course"]
            rm.export_csv("students_report", data, headers)
            rm.export_pdf("students_report", "Student Report", data, headers)

        elif choice == "Courses CSV/PDF":
            data = [{"ID": k, "Name": v["name"], "Description": v["description"]} for k, v in cm.courses.items()]
            headers = ["ID", "Name", "Description"]
            rm.export_csv("courses_report", data, headers)
            rm.export_pdf("courses_report", "Course Report", data, headers)

        elif choice == "Enrollments CSV/PDF":
            data = []
            for cid, students in em.enrollments.items():
                for sid in students:
                    data.append({"Course ID": cid, "Student ID": sid})
            headers = ["Course ID", "Student ID"]
            rm.export_csv("enrollments_report", data, headers)
            rm.export_pdf("enrollments_report", "Enrollment Report", data, headers)

        elif choice == "Library CSV/PDF":
            data = []
            for bid, book in lm.books.items():
                available = lm.get_available_copies(bid)
                data.append({"Book ID": bid, "Title": book["title"], "Author": book["author"], "Copies": book["copies"], "Available": available})
            headers = ["Book ID", "Title", "Author", "Copies", "Available"]
            rm.export_csv("library_report", data, headers)
            rm.export_pdf("library_report", "Library Report", data, headers)
        else:
            break

if __name__ == "__main__":
    main_menu()
