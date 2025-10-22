
from data_manager import DataManager
from input_helper import confirm
from colorama import Fore

class EnrollmentManager:
    """
    Manage student-course enrollments.
    Data stored via DataManager (JSON): {course_id: [student_id,...]}
    """

    def __init__(self, data_file="data/enrollments.json"):
        self.dm = DataManager(data_file)
        self.enrollments = self.dm.read_json() or {}

    # ➕ Enroll Student
    def enroll(self, student_id: str, course_id: str):
        if course_id not in self.enrollments:
            self.enrollments[course_id] = []
        if student_id in self.enrollments[course_id]:
            print(Fore.YELLOW + f"⚠️ Student {student_id} already enrolled in {course_id}.")
            return
        self.enrollments[course_id].append(student_id)
        self._save()
        print(Fore.GREEN + f"✅ Student {student_id} enrolled in course {course_id}.")

    # 🗑 Unenroll Student
    def unenroll(self, student_id: str, course_id: str):
        if course_id not in self.enrollments or student_id not in self.enrollments[course_id]:
            print(Fore.RED + f"⚠️ Student {student_id} not enrolled in {course_id}.")
            return
        if confirm(f"Are you sure you want to unenroll {student_id} from {course_id}? (y/n): "):
            self.enrollments[course_id].remove(student_id)
            self._save()
            print(Fore.GREEN + f"🗑️ Student {student_id} unenrolled from {course_id}.")
        else:
            print(Fore.YELLOW + "❌ Action cancelled.")

    # 📋 List Enrollments
    def list_enrollments(self):
        if not self.enrollments:
            print(Fore.YELLOW + "📭 No enrollments found.")
            return
        print(Fore.MAGENTA + "\n📚 Course Enrollments:")
        for cid, students in self.enrollments.items():
            print(f" • Course {cid}: {', '.join(students) if students else 'No students'}")

    # 💾 Save Helper
    def _save(self):
        self.dm.write_json(self.enrollments)