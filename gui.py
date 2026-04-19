import mysql.connector


def test_connection_and_query():
    print("\n[TEST] Starting DB test...")

    print("[TEST] Connecting to database...")

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
        print("[TEST] ✅ Connected to MySQL")

    cursor = conn.cursor()

    # -------------------------------
    # TEST QUERY
    # -------------------------------
    query = "SELECT courseId, cname FROM course LIMIT 5"

    print("\n[TEST] Executing query:")
    print(query)

    cursor.execute(query)

    results = cursor.fetchall()

    print("\n[TEST] Query Results:")
    for row in results:
        print(row)

    print("\n[TEST] ✅ Query executed successfully")

    cursor.close()
    conn.close()
    print("\n[TEST] Connection closed")



test_connection_and_query()