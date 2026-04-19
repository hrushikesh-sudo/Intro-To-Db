import mysql.connector

# -------------------------------
# DB CONNECTION
# -------------------------------
def get_connection():
    print("\n[DB] Attempting connection...")

    try:
        
        conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="academic_insti",
        port=3306,
        connection_timeout=5,
        use_pure=True  
    )

        if conn.is_connected():
            print("[DB] ✅ Connection established")
            return conn
        else:
            print("[DB] ❌ Connection failed")
            return None

    except Exception as e:
        print("[DB] ❌ Connection error:", e)
        return None


# -------------------------------
# INITIAL CONNECTION CHECK
# -------------------------------
def check_db_connection():
    print("\n[INIT] Checking database connectivity...")

    conn = get_connection()
    if conn is None:
        print("[INIT] ❌ Database NOT reachable. Exiting.")
        return False

    conn.close()
    print("[INIT] ✅ Database is reachable")
    return True


# -------------------------------
# DEBUG QUERY PRINT
# -------------------------------
def debug_query(query, params=None):
    print("\n[SQL] -----------------------------")
    print("[SQL] Query:", query.strip())
    if params:
        print("[SQL] Params:", params)


# -------------------------------
# VALIDATIONS
# -------------------------------
def course_exists(course_id):
    print(f"\n[FUNC] course_exists({course_id})")

    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    query = "SELECT * FROM course WHERE courseId = %s"
    params = (course_id,)

    debug_query(query, params)
    cursor.execute(query, params)

    result = cursor.fetchone()
    print("[SQL] Result:", result)

    cursor.close()
    conn.close()
    print("[DB] Connection closed")

    return result is not None


def teacher_exists(teacher_id):
    print(f"\n[FUNC] teacher_exists({teacher_id})")

    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    query = "SELECT * FROM professor WHERE empId = %s"
    params = (teacher_id,)

    debug_query(query, params)
    cursor.execute(query, params)

    result = cursor.fetchone()
    print("[SQL] Result:", result)

    cursor.close()
    conn.close()
    print("[DB] Connection closed")

    return result is not None

def department_exists(dept_id):
    print(f"\n[FUNC] department_exists({dept_id})")

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM department WHERE deptId = %s"
    params = (dept_id,)

    debug_query(query, params)
    cursor.execute(query, params)

    result = cursor.fetchone()
    print("[SQL] Result:", result)

    cursor.close()
    conn.close()

    return result is not None
def add_course(dept_id, course_id, teacher_id, classroom):
    print(f"\n[FUNC] add_course({dept_id}, {course_id}, {teacher_id}, {classroom})")

    # -------------------------------
    # VALIDATIONS
    # -------------------------------
    if not department_exists(dept_id):
        return "❌ Department does not exist"

    if not course_exists(course_id):
        return "❌ Course does not exist"

    if not teacher_exists(teacher_id):
        return "❌ Teacher does not exist"

    conn = get_connection()
    if conn is None:
        return "❌ DB Connection failed"

    cursor = conn.cursor()

    try:
        # -------------------------------
        # CHECK COURSE BELONGS TO DEPT
        # -------------------------------
        query1 = """
            SELECT *
            FROM course
            WHERE courseId = %s AND deptNo = %s
        """
        params1 = (course_id, dept_id)

        debug_query(query1, params1)
        cursor.execute(query1, params1)

        if cursor.fetchone() is None:
            return "❌ Course does not belong to this department"

        # -------------------------------
        # CHECK TEACHER BELONGS TO DEPT
        # -------------------------------
        query2 = """
            SELECT *
            FROM professor
            WHERE empId = %s AND deptNo = %s
        """
        params2 = (teacher_id, dept_id)

        debug_query(query2, params2)
        cursor.execute(query2, params2)

        if cursor.fetchone() is None:
            return "❌ Teacher does not belong to this department"

        # -------------------------------
        # INSERT / UPDATE TEACHING
        # -------------------------------
        query3 = """
            INSERT INTO teaching (empId, courseId, sem, year, classRoom)
            VALUES (%s, %s, 'even', 2006, %s)
            ON DUPLICATE KEY UPDATE
                empId = VALUES(empId),
                classRoom = VALUES(classRoom)
        """
        params3 = (teacher_id, course_id, classroom)

        debug_query(query3, params3)
        cursor.execute(query3, params3)

        conn.commit()

        print("[SUCCESS] ✅ Course offering updated for even 2006")
        return "✅ Course offering updated successfully"

    except Exception as e:
        conn.rollback()
        print("[ERROR] ❌", e)
        return f"❌ Error: {e}"

    finally:
        cursor.close()
        conn.close()
        print("[DB] Connection closed")


def student_exists(roll_no):
    print(f"\n[FUNC] student_exists({roll_no})")

    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    query = "SELECT * FROM student WHERE rollNo = %s"
    params = (roll_no,)

    debug_query(query, params)
    cursor.execute(query, params)

    result = cursor.fetchone()
    print("[SQL] Result:", result)

    cursor.close()
    conn.close()
    print("[DB] Connection closed")

    return result is not None


def check_prerequisites(roll_no, course_id):
    print(f"\n[FUNC] check_prerequisites({roll_no}, {course_id})")

    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        # -------------------------------
        # STEP 1: Get all prerequisites
        # -------------------------------
        query1 = """
            SELECT preReqCourse
            FROM preRequisite
            WHERE courseId = %s
        """
        params1 = (course_id,)

        debug_query(query1, params1)
        cursor.execute(query1, params1)

        prereqs = cursor.fetchall()
        print("[INFO] Prerequisites:", prereqs)

        # If no prerequisites → allow
        if not prereqs:
            print("[INFO] No prerequisites → allowed")
            return True

        # -------------------------------
        # STEP 2: Check each prerequisite
        # -------------------------------
        for (pre_course,) in prereqs:
            print(f"[CHECK] Checking prerequisite: {pre_course}")

            query2 = """
                SELECT *
                FROM enrollment
                WHERE rollNo = %s
                  AND courseId = %s
                  AND grade != 'U'
            """
            params2 = (roll_no, pre_course)

            debug_query(query2, params2)
            cursor.execute(query2, params2)

            result = cursor.fetchone()
            print("[RESULT]:", result)

            if result is None:
                print(f"[FAIL] ❌ Missing or failed prerequisite: {pre_course}")
                return False

        print("[SUCCESS] ✅ All prerequisites satisfied")
        return True

    except Exception as e:
        print("[ERROR] ❌", e)
        return False

    finally:
        cursor.close()
        conn.close()
        print("[DB] Connection closed")


# -------------------------------
# ENROLL STUDENT
# -------------------------------
def enroll_student(roll_no, course_id):
    print(f"\n[FUNC] enroll_student({roll_no}, {course_id})")

    if not student_exists(roll_no):
        print("[ERROR] ❌ Student does not exist")
        return "❌ Student does not exist"

    if not course_exists(course_id):
        print("[ERROR] ❌ Course does not exist")
        return "❌ Course does not exist"

    if not check_prerequisites(roll_no, course_id):
        print("[ERROR] ❌ Prerequisites not satisfied")
        return "❌ Prerequisites not satisfied"

    conn = get_connection()
    if conn is None:
        return "❌ DB Connection failed"

    cursor = conn.cursor()

    query = """
        INSERT INTO enrollment (rollNo, courseId, sem, year, grade)
        VALUES (%s, %s, 'even', 2006, NULL)
    """
    params = (roll_no, course_id)

    try:
        debug_query(query, params)
        cursor.execute(query, params)

        conn.commit()

        print("[SQL] Rows affected:", cursor.rowcount)
        print("[SUCCESS] ✅ Enrollment done")

        return "✅ Enrollment successful"

    except Exception as e:
        print("[ERROR] ❌", e)
        return f"❌ Error: {e}"

    finally:
        cursor.close()
        conn.close()
        print("[DB] Connection closed")