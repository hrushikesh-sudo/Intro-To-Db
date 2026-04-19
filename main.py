import streamlit as st
from functions import add_course, enroll_student, check_db_connection

st.set_page_config(page_title="Academic DB App")

st.title("🎓 Academic Institute Management System")

# -------------------------------
# CHECK DB AT STARTUP
# -------------------------------
if not check_db_connection():
    st.error("❌ Cannot connect to database. Check terminal logs.")
    st.stop()
else:
    st.success("✅ Database connected")


menu = st.sidebar.selectbox(
    "Choose Operation",
    ["Add Course", "Enroll Student"]
)

# -------------------------------
# ADD COURSE
# -------------------------------
if menu == "Add Course":
    st.header("➕ Add Course Offering")

    dept_id = st.text_input("Department ID")
    course_id = st.text_input("Course ID")
    teacherid = st.text_input("Teacher ID")
    classroom = st.text_input("classroom")

    if st.button("Add Course"):
        result = add_course(dept_id, course_id, teacherid, classroom)
        st.write(result)


# -------------------------------
# ENROLL STUDENT
# -------------------------------
elif menu == "Enroll Student":
    st.header("🧑‍🎓 Enroll Student")

    roll_no = st.text_input("Roll Number")
    course_id = st.text_input("Course ID")

    if st.button("Enroll"):
        result = enroll_student(roll_no, course_id)
        st.write(result)