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
        use_pure=True   # 👈 IMPORTANT
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

def add_course(dept_id, course_id, course_name, credits):
    print(f"\n[FUNC] add_course({dept_id}, {course_id}, {course_name}, {credits})")

    # -------------------------------
    # VALIDATIONS
    # -------------------------------
    if not department_exists(dept_id):
        print("[ERROR] ❌ Department does not exist")
        return "❌ Department does not exist"


    if course_exists(course_id):
        print("[ERROR] ❌ Course already exists")
        return "❌ Course already exists"

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------------
    # INSERT INTO course table
    # -------------------------------
    query = """
        INSERT INTO course (courseId, cname, credits, deptNo)
        VALUES (%s, %s, %s, %s)
    """
    params = (course_id, course_name, credits, dept_id)

    try:
        debug_query(query, params)
        cursor.execute(query, params)

        conn.commit()

        print("[SUCCESS] ✅ Course added to course table")

    except Exception as e:
        print("[ERROR] ❌", e)
        conn.close()
        return f"❌ Error: {e}"

    finally:
        cursor.close()
        conn.close()
        print("[DB] Connection closed")

    return "✅ Course added successfully with teacher"


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