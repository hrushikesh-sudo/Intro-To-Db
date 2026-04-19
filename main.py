import argparse

from functions import add_course_db, enroll_student_db
from gui import start_gui


def run_cli():
    while True:
        print("\nAcademic DB App - Assn 4A")
        print("1. Add or update course offering")
        print("2. Enroll student")
        print("3. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            dept_id = input("Department ID: ").strip()
            course_id = input("Course ID: ").strip()
            teacher_id = input("Teacher ID: ").strip()
            classroom = input("Classroom: ").strip()
            print(add_course_db(dept_id, course_id, teacher_id, classroom))
        elif choice == "2":
            dept_id = input("Department ID: ").strip()
            roll_no = input("Roll No: ").strip()
            course_ids = input("Course IDs (comma separated): ").split(",")
            print(enroll_student_db(dept_id, roll_no, course_ids))
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Academic institute assignment app")
    parser.add_argument(
        "--mode",
        choices=["gui", "cli"],
        default="gui",
        help="Choose GUI or CLI mode.",
    )
    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    else:
        start_gui()
