
from data_manager import DataManager
from input_helper import get_str, confirm
from colorama import Fore

class CourseManager:
    """
    Manage courses: add, remove, list, search.
    Data stored via DataManager (JSON).
    """

    def __init__(self, data_file="data/courses.json"):
        self.dm = DataManager(data_file)
        self.courses = self.dm.read_json() or {}  # {course_id: {"name":..., "description":...}}

    # ➕ Add Course
    def add_course(self, course_id: str, name: str, description: str = ""):
        if course_id in self.courses:
            print(Fore.YELLOW + f"⚠️ Course ID {course_id} already exists.")
            return
        self.courses[course_id] = {"name": name, "description": description}
        self._save()
        print(Fore.GREEN + f"✅ Added course: {name}")

    # 🗑 Remove Course
    def remove_course(self, course_id: str):
        if course_id not in self.courses:
            print(Fore.RED + f"⚠️ Course ID {course_id} not found.")
            return
        if confirm(f"Are you sure you want to remove course {course_id}? (y/n): "):
            removed = self.courses.pop(course_id)
            self._save()
            print(Fore.GREEN + f"🗑️ Removed course: {removed['name']}")
        else:
            print(Fore.YELLOW + "❌ Action cancelled.")

    # 📋 List Courses
    def list_courses(self):
        if not self.courses:
            print(Fore.YELLOW + "📭 No courses available.")
            return
        print(Fore.MAGENTA + "\n📚 Current Courses:")
        for cid, info in self.courses.items():
            print(f" • ID: {cid} | Name: {info['name']} | Description: {info['description']}")

    # 🔍 Find Course
    def find_course(self, course_id: str):
        course = self.courses.get(course_id)
        if course:
            print(f"👤 Found course: {course['name']} ({course['description']})")
            return course
        print(Fore.RED + f"⚠️ Course ID {course_id} not found.")
        return None

    # 💾 Save Helper
    def _save(self):
        self.dm.write_json(self.courses)
