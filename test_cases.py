from db import get_connection
from functions import (
    TARGET_SEMESTER,
    TARGET_TERM_LABEL,
    TARGET_YEAR,
    add_course_db,
    enroll_student_db,
)


def _run_sql(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def _cleanup_enrollment(roll_no, course_id):
    _run_sql(
        """
        DELETE FROM enrollment
        WHERE rollNo = %s AND courseId = %s
          AND LOWER(sem) = %s AND year = %s
        """,
        (roll_no, course_id, TARGET_SEMESTER, TARGET_YEAR),
    )


def _cleanup_teaching(emp_id, course_id):
    _run_sql(
        """
        DELETE FROM teaching
        WHERE empId = %s AND courseId = %s
          AND LOWER(sem) = %s AND year = %s
        """,
        (emp_id, course_id, TARGET_SEMESTER, TARGET_YEAR),
    )


def _print_result(name, passed, details):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    print(f"  {details}")


def _check_contains(name, actual, expected_substrings):
    missing = [text for text in expected_substrings if text not in actual]
    if missing:
        _print_result(
            name,
            False,
            f"Expected to contain {missing}, but got: {actual}",
        )
        return False

    _print_result(name, True, actual)
    return True


def test_add_course_success_insert():
    name = "Add course offering: valid insert"
    _cleanup_teaching("CS07", "CS635")
    result = add_course_db("9", "CS635", "CS07", "LAB-A1")
    passed = _check_contains(name, result, ["successfully", TARGET_TERM_LABEL])
    _cleanup_teaching("CS07", "CS635")
    return passed


def test_add_course_success_update():
    name = "Add course offering: update existing row"
    _cleanup_teaching("CS07", "CS635")
    add_course_db("9", "CS635", "CS07", "LAB-A1")
    result = add_course_db("9", "CS635", "CS07", "LAB-A2")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT classRoom
            FROM teaching
            WHERE empId = %s AND courseId = %s
              AND LOWER(sem) = %s AND year = %s
            """,
            ("CS07", "CS635", TARGET_SEMESTER, TARGET_YEAR),
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    passed = (
        "successfully" in result.lower()
        and row is not None
        and row[0] == "LAB-A2"
    )
    if passed:
        _print_result(name, True, result)
    else:
        _print_result(name, False, f"Result: {result}; classroom row: {row}")

    _cleanup_teaching("CS07", "CS635")
    return passed


def test_add_course_invalid_department():
    return _check_contains(
        "Add course offering: invalid department",
        add_course_db("99", "CS635", "CS07", "LAB-A1"),
        ["Invalid Department ID."],
    )


def test_add_course_invalid_course_for_department():
    return _check_contains(
        "Add course offering: invalid course for department",
        add_course_db("9", "451", "CS07", "LAB-A1"),
        ["Invalid Course ID for the given department."],
    )


def test_add_course_invalid_teacher_for_department():
    return _check_contains(
        "Add course offering: invalid teacher for department",
        add_course_db("9", "CS635", "15347", "LAB-A1"),
        ["Invalid Teacher ID for the given department."],
    )


def test_add_course_empty_fields():
    return _check_contains(
        "Add course offering: empty fields",
        add_course_db("9", "", "CS07", "LAB-A1"),
        ["All fields are required."],
    )


def test_enroll_success():
    name = "Enroll student: valid prerequisite satisfied"
    _cleanup_teaching("14365", "760")
    _cleanup_enrollment("10454", "760")

    offering_result = add_course_db("8", "760", "14365", "R20")
    result = enroll_student_db("10454", ["760"])
    passed = _check_contains(name, offering_result, ["successfully"]) and _check_contains(
        name, result, ["Enrolled successfully: 760"]
    )

    _cleanup_enrollment("10454", "760")
    _cleanup_teaching("14365", "760")
    return passed


def test_enroll_missing_prerequisite():
    name = "Enroll student: missing prerequisite"
    _cleanup_teaching("14365", "760")
    _cleanup_enrollment("1000", "760")

    offering_result = add_course_db("8", "760", "14365", "R20")
    result = enroll_student_db("1000", ["760"])
    passed = _check_contains(name, offering_result, ["successfully"]) and _check_contains(
        name, result, ["760: missing prerequisites (169)"]
    )

    _cleanup_enrollment("1000", "760")
    _cleanup_teaching("14365", "760")
    return passed


def test_enroll_invalid_student():
    return _check_contains(
        "Enroll student: invalid student",
        enroll_student_db("ZZ999", ["760"]),
        ["Invalid Student ID."],
    )


def test_enroll_invalid_course():
    return _check_contains(
        "Enroll student: invalid course",
        enroll_student_db("10454", ["XYZ999"]),
        ["XYZ999: invalid course"],
    )


def test_enroll_course_not_offered():
    _cleanup_teaching("CS07", "CS635")
    return _check_contains(
        "Enroll student: course not offered",
        enroll_student_db("7M001", ["CS635"]),
        [f"CS635: not offered in {TARGET_TERM_LABEL}"],
    )


def test_enroll_duplicate():
    name = "Enroll student: duplicate enrollment"
    _cleanup_teaching("14365", "760")
    _cleanup_enrollment("10454", "760")

    offering_result = add_course_db("8", "760", "14365", "R20")
    first_result = enroll_student_db("10454", ["760"])
    result = enroll_student_db("10454", ["760"])
    passed = (
        _check_contains(name, offering_result, ["successfully"])
        and _check_contains(name, first_result, ["Enrolled successfully: 760"])
        and _check_contains(
            name,
            result,
            [f"760: already enrolled in {TARGET_TERM_LABEL}"],
        )
    )

    _cleanup_enrollment("10454", "760")
    _cleanup_teaching("14365", "760")
    return passed


def test_enroll_mixed_list():
    name = "Enroll student: mixed valid and invalid courses"
    _cleanup_teaching("14365", "760")
    _cleanup_enrollment("10454", "760")

    offering_result = add_course_db("8", "760", "14365", "R20")
    result = enroll_student_db("10454", ["760", "XYZ999"])
    passed = _check_contains(name, offering_result, ["successfully"]) and _check_contains(
        name,
        result,
        ["Enrolled successfully: 760", "XYZ999: invalid course"],
    )

    _cleanup_enrollment("10454", "760")
    _cleanup_teaching("14365", "760")
    return passed


def test_enroll_empty_inputs():
    return _check_contains(
        "Enroll student: empty input",
        enroll_student_db("", []),
        ["Roll No and at least one Course ID are required."],
    )


def main():
    tests = [
        test_add_course_success_insert,
        test_add_course_success_update,
        test_add_course_invalid_department,
        test_add_course_invalid_course_for_department,
        test_add_course_invalid_teacher_for_department,
        test_add_course_empty_fields,
        test_enroll_success,
        test_enroll_missing_prerequisite,
        test_enroll_invalid_student,
        test_enroll_invalid_course,
        test_enroll_course_not_offered,
        test_enroll_duplicate,
        test_enroll_mixed_list,
        test_enroll_empty_inputs,
    ]

    print(f"Running database tests for {TARGET_TERM_LABEL}")
    print("-" * 60)

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            _print_result(test.__name__, False, f"Unexpected exception: {exc}")

    print("-" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
