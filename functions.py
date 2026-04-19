from db import get_connection

TARGET_SEMESTER = "Even"
TARGET_YEAR = 2006
PASSING_GRADES = {"A", "B", "C", "D", "E", "S"}


def _course_exists_for_department(cursor, dept_id, course_id):
    cursor.execute(
        """
        SELECT cname
        FROM course
        WHERE courseId = %s AND deptNo = %s
        """,
        (course_id, dept_id),
    )
    return cursor.fetchone()


def _teacher_exists_for_department(cursor, dept_id, teacher_id):
    cursor.execute(
        """
        SELECT name
        FROM professor
        WHERE empId = %s AND deptNo = %s
        """,
        (teacher_id, dept_id),
    )
    return cursor.fetchone()


def _student_exists_for_department(cursor, dept_id, roll_no):
    cursor.execute(
        """
        SELECT name
        FROM student
        WHERE rollNo = %s AND deptNo = %s
        """,
        (roll_no, dept_id),
    )
    return cursor.fetchone()


def _get_prerequisites(cursor, course_id):
    cursor.execute(
        """
        SELECT preReqCourse
        FROM prerequisite
        WHERE courseId = %s
        ORDER BY preReqCourse
        """,
        (course_id,),
    )
    return [row[0] for row in cursor.fetchall()]


def _has_passed_course(cursor, roll_no, course_id):
    cursor.execute(
        """
        SELECT grade
        FROM enrollment
        WHERE rollNo = %s AND courseId = %s
        """,
        (roll_no, course_id),
    )

    for (grade,) in cursor.fetchall():
        if grade and grade.strip().upper() in PASSING_GRADES:
            return True

    return False


def _missing_prerequisites(cursor, roll_no, course_id):
    prerequisites = _get_prerequisites(cursor, course_id)
    return [
        prereq for prereq in prerequisites if not _has_passed_course(cursor, roll_no, prereq)
    ]


def add_course_db(dept_id, course_id, teacher_id, classroom):
    dept_id = dept_id.strip()
    course_id = course_id.strip()
    teacher_id = teacher_id.strip()
    classroom = classroom.strip()

    if not all([dept_id, course_id, teacher_id, classroom]):
        return "All fields are required."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM department WHERE deptId = %s", (dept_id,))
        if cursor.fetchone() is None:
            return "Invalid Department ID."

        if _course_exists_for_department(cursor, dept_id, course_id) is None:
            return "Invalid Course ID for the given department."

        if _teacher_exists_for_department(cursor, dept_id, teacher_id) is None:
            return "Invalid Teacher ID for the given department."

        cursor.execute(
            """
            SELECT classRoom
            FROM teaching
            WHERE empId = %s AND courseId = %s
              AND LOWER(sem) = %s AND year = %s
            """,
            (teacher_id, course_id, TARGET_SEMESTER.lower(), TARGET_YEAR),
        )
        existing_teacher_assignment = cursor.fetchone()
        if existing_teacher_assignment is not None:
            cursor.execute(
                """
                UPDATE teaching
                SET classRoom = %s, sem = %s, year = %s
                WHERE empId = %s AND courseId = %s
                  AND LOWER(sem) = %s AND year = %s
                """,
                (
                    classroom,
                    TARGET_SEMESTER,
                    TARGET_YEAR,
                    teacher_id,
                    course_id,
                    TARGET_SEMESTER.lower(),
                    TARGET_YEAR,
                ),
            )
            conn.commit()
            return "Course offering updated successfully."

        cursor.execute(
            """
            SELECT empId
            FROM teaching
            WHERE courseId = %s AND LOWER(sem) = %s AND year = %s
            """,
            (course_id, TARGET_SEMESTER.lower(), TARGET_YEAR),
        )
        current_course_assignment = cursor.fetchone()

        if current_course_assignment is not None:
            cursor.execute(
                """
                UPDATE teaching
                SET empId = %s, classRoom = %s, sem = %s, year = %s
                WHERE courseId = %s AND LOWER(sem) = %s AND year = %s
                """,
                (
                    teacher_id,
                    classroom,
                    TARGET_SEMESTER,
                    TARGET_YEAR,
                    course_id,
                    TARGET_SEMESTER.lower(),
                    TARGET_YEAR,
                ),
            )
            conn.commit()
            return "Course offering updated successfully."

        cursor.execute(
            """
            INSERT INTO teaching (empId, courseId, sem, year, classRoom)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (teacher_id, course_id, TARGET_SEMESTER, TARGET_YEAR, classroom),
        )
        conn.commit()
        return "Course offering added successfully."
    finally:
        cursor.close()
        conn.close()


def enroll_student_db(dept_id, roll_no, course_list):
    dept_id = dept_id.strip()
    roll_no = roll_no.strip()
    cleaned_courses = [course.strip() for course in course_list if course.strip()]

    if not dept_id or not roll_no or not cleaned_courses:
        return "Department ID, Roll No, and at least one Course ID are required."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM department WHERE deptId = %s", (dept_id,))
        if cursor.fetchone() is None:
            return "Invalid Department ID."

        if _student_exists_for_department(cursor, dept_id, roll_no) is None:
            return "Invalid Student ID for the given department."

        enrolled = []
        skipped = []

        for course_id in cleaned_courses:
            if _course_exists_for_department(cursor, dept_id, course_id) is None:
                skipped.append(f"{course_id}: invalid course for department")
                continue

            cursor.execute(
                """
                SELECT 1
                FROM teaching
                WHERE courseId = %s AND LOWER(sem) = %s AND year = %s
                """,
                (course_id, TARGET_SEMESTER.lower(), TARGET_YEAR),
            )
            if cursor.fetchone() is None:
                skipped.append(f"{course_id}: not offered in Even 2006")
                continue

            cursor.execute(
                """
                SELECT grade
                FROM enrollment
                WHERE rollNo = %s AND courseId = %s
                  AND LOWER(sem) = %s AND year = %s
                """,
                (roll_no, course_id, TARGET_SEMESTER.lower(), TARGET_YEAR),
            )
            existing = cursor.fetchone()
            if existing is not None:
                skipped.append(f"{course_id}: already enrolled in Even 2006")
                continue

            missing = _missing_prerequisites(cursor, roll_no, course_id)
            if missing:
                skipped.append(
                    f"{course_id}: missing prerequisites ({', '.join(missing)})"
                )
                continue

            cursor.execute(
                """
                INSERT INTO enrollment (rollNo, courseId, sem, year, grade)
                VALUES (%s, %s, %s, %s, NULL)
                """,
                (roll_no, course_id, TARGET_SEMESTER.lower(), TARGET_YEAR),
            )
            enrolled.append(course_id)

        conn.commit()

        messages = []
        if enrolled:
            messages.append("Enrolled successfully: " + ", ".join(enrolled))
        if skipped:
            messages.append("Skipped: " + "; ".join(skipped))

        return "\n".join(messages) if messages else "No enrollment changes made."
    finally:
        cursor.close()
        conn.close()
