import tkinter as tk
from tkinter import messagebox

from functions import (
    TARGET_TERM_LABEL,
    add_course_db,
    enroll_student_db,
)


def _is_error_message(result):
    lowered = result.lower()
    error_prefixes = (
        "invalid",
        "all fields",
        "roll no",
        "error",
        "failed",
        "duplicate",
        "cannot",
    )
    return lowered.startswith(error_prefixes)


def start_gui():
    root = tk.Tk()
    root.title("Academic DB App - Assn 4A")
    root.geometry("560x460")

    frame1 = tk.Frame(root)
    frame2 = tk.Frame(root)

    for frame in (frame1, frame2):
        frame.place(relwidth=1, relheight=1)

    def show_frame(frame):
        frame.tkraise()

    tk.Label(
        frame1,
        text=f"Add Course Offering\n{TARGET_TERM_LABEL}",
        font=("Arial", 16),
        justify="center",
    ).pack(pady=12)

    dept_entry = tk.Entry(frame1)
    course_entry = tk.Entry(frame1)
    teacher_entry = tk.Entry(frame1)
    room_entry = tk.Entry(frame1)

    tk.Label(frame1, text="Department ID").pack()
    dept_entry.pack()

    tk.Label(frame1, text="Course ID").pack()
    course_entry.pack()

    tk.Label(frame1, text="Teacher ID").pack()
    teacher_entry.pack()

    tk.Label(frame1, text="Classroom").pack()
    room_entry.pack()

    def add_course():
        result = add_course_db(
            dept_entry.get(),
            course_entry.get(),
            teacher_entry.get(),
            room_entry.get(),
        )
        if "successfully" in result.lower():
            messagebox.showinfo("Success", result)
        else:
            messagebox.showerror("Error", result)

    tk.Button(frame1, text="Add / Update Course", command=add_course).pack(pady=10)
    tk.Button(frame1, text="Go to Enrollment", command=lambda: show_frame(frame2)).pack()

    tk.Label(
        frame2,
        text=f"Student Enrollment\n{TARGET_TERM_LABEL}",
        font=("Arial", 16),
        justify="center",
    ).pack(pady=12)

    roll_entry = tk.Entry(frame2)
    course_list_entry = tk.Entry(frame2, width=40)


    tk.Label(frame2, text="Roll No").pack()
    roll_entry.pack()

    tk.Label(frame2, text="Course IDs (comma separated)").pack()
    course_list_entry.pack()

    def enroll():
        result = enroll_student_db(
            roll_entry.get(),
            course_list_entry.get().split(","),
        )
        if _is_error_message(result):
            messagebox.showerror("Error", result)
        else:
            messagebox.showinfo("Enrollment Result", result)

    tk.Button(frame2, text="Enroll Student", command=enroll).pack(pady=10)
    tk.Button(frame2, text="Back", command=lambda: show_frame(frame1)).pack()

    show_frame(frame1)
    root.mainloop()
