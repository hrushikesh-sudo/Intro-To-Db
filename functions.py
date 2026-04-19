from db import get_connection

TARGET_SEMESTER = "even"
TARGET_YEAR = 2006
TARGET_TERM_LABEL = "Even Semester 2006"
PASSING_GRADES = {"A", "B", "C", "D", "E", "S"}


def _course_exists(cursor, course_id):
    cursor.execute(
        """
        SELECT cname
        FROM course
        WHERE courseId = %s
        """,
        (course_id,),
    )
    return cursor.fetchone()


def _course_exists_in_dept(cursor, course_id, dept_id):
    cursor.execute(
        """
        SELECT cname
        FROM course
        WHERE courseId = %s AND deptNo = %s
        """,
        (course_id, dept_id),
    )
    return cursor.fetchone()


def _teacher_exists(cursor, teacher_id):
    cursor.execute(
        """
        SELECT name
        FROM professor
        WHERE empId = %s
        """,
        (teacher_id,),
    )
    return cursor.fetchone()


def _teacher_exists_in_dept(cursor, teacher_id, dept_id):
    cursor.execute(
        """
        SELECT name
        FROM professor
        WHERE empId = %s AND deptNo = %s
        """,
        (teacher_id, dept_id),
    )
    return cursor.fetchone()


def _student_exists(cursor, roll_no):
    cursor.execute(
        """
        SELECT name
        FROM student
        WHERE rollNo = %s
        """,
        (roll_no,),
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
          AND (
                year < %s
                OR (year = %s AND LOWER(sem) = 'odd')
              )
        """,
        (roll_no, course_id, TARGET_YEAR, TARGET_YEAR),
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


# -------------------------
# 1. ADD COURSE 
# -------------------------
def add_course_db(dept_id, course_id, teacher_id, classroom):
    dept_id = dept_id.strip()
    course_id = course_id.strip()
    teacher_id = teacher_id.strip()
    classroom = classroom.strip()

    if not all([dept_id, course_id, teacher_id, classroom]):
        return "All fields are required."

    try:
        conn = get_connection()
    except Exception as e:
        return f"Database connection failed: {e}"

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM department WHERE deptId = %s", (dept_id,))
        if cursor.fetchone() is None:
            return "Invalid Department ID."

        if _course_exists_in_dept(cursor, course_id, dept_id) is None:
            return "Invalid Course ID for the given department."

        if _teacher_exists_in_dept(cursor, teacher_id, dept_id) is None:
            return "Invalid Teacher ID for the given department."

        cursor.execute(
            """
            INSERT INTO teaching (empId, courseId, sem, year, classRoom)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE classRoom = VALUES(classRoom)
            """,
            (teacher_id, course_id, TARGET_SEMESTER, TARGET_YEAR, classroom),
        )
        conn.commit()
        return f"Course offering added/updated successfully for {TARGET_TERM_LABEL}."

    except Exception as e:
        conn.rollback()
        return f"A database error occurred: {e}"
    finally:
        cursor.close()
        conn.close()


# -------------------------
# 2. ENROLL STUDENT (UPDATED)
# -------------------------
def enroll_student_db(roll_no, course_list):
    roll_no = roll_no.strip()
    cleaned_courses = [course.strip() for course in course_list if course.strip()]

    if not roll_no or not cleaned_courses:
        return "Roll No and at least one Course ID are required."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if _student_exists(cursor, roll_no) is None:
            return "Invalid Student ID."

        enrolled = []
        skipped = []

        for course_id in cleaned_courses:
            # this can be done efficiently by a single sql query but kept as it is for simplicity

            # check course exists
            if _course_exists(cursor, course_id) is None:
                skipped.append(f"{course_id}: invalid course")
                continue

            # check course is offered in target sem/year
            cursor.execute(
                """
                SELECT 1
                FROM teaching
                WHERE courseId = %s AND LOWER(sem) = %s AND year = %s
                """,
                (course_id, TARGET_SEMESTER, TARGET_YEAR),
            )
            if cursor.fetchone() is None:
                skipped.append(f"{course_id}: not offered in {TARGET_TERM_LABEL}")
                continue

            # already enrolled?
            cursor.execute(
                """
                SELECT 1
                FROM enrollment
                WHERE rollNo = %s AND courseId = %s
                  AND LOWER(sem) = %s AND year = %s
                """,
                (roll_no, course_id, TARGET_SEMESTER, TARGET_YEAR),
            )
            if cursor.fetchone() is not None:
                skipped.append(f"{course_id}: already enrolled in {TARGET_TERM_LABEL}")
                continue

            # prerequisite check
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
                (roll_no, course_id, TARGET_SEMESTER, TARGET_YEAR),
            )
            enrolled.append(course_id)

        conn.commit()

        messages = []
        if enrolled:
            messages.append("Enrolled successfully: " + ", ".join(enrolled))
        if skipped:
            messages.append("Skipped: " + "; ".join(skipped))

        return "\n".join(messages) if messages else "No enrollment changes made."

    except Exception as e:
        conn.rollback()
        return str(e)
    finally:
        cursor.close()
        conn.close()
