# Assignment 4A - Academic Institute Application

Python application for the `academic_insti` MySQL database with the two required features:

1. Add or update a course offering for the Even semester of 2006.
2. Enroll a student into one or more courses for the same semester after prerequisite validation.


## Requirements

- Python 3
- MySQL Server
- Python package `mysql-connector-python`

## Database Setup

Import the corrected SQL dump:

```bash
mysql -u root -p < ../academic_insti.sql
```

This creates the `academic_insti` database and loads the sample data.

## Python Setup

Install the dependency:

```bash
pip install mysql-connector-python
```

Set database credentials using environment variables:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_NAME=academic_insti
```

## Run The Application

GUI mode:

```bash
python main.py
```

CLI mode:

```bash
python main.py --mode cli
```

## Functionality

### 1. Add / Update Course Offering

Inputs:

- Department ID
- Course ID
- Teacher ID
- Classroom

Checks performed:

- Department exists
- Course belongs to that department
- Teacher belongs to that department

Effect:

- Adds or updates the `teaching` entry for `Even Semester 2006`

### 2. Student Enrollment

Inputs:

- Roll No
- Course IDs (comma separated in the CLI/GUI)

Checks performed:

- Student exists
- Course exists
- Course is offered in `Even Semester 2006`
- Student has passed all prerequisite courses
- Student is not already enrolled in that course in `Even Semester 2006`

Effect:

- Inserts rows into `enrollment` with `sem='even'`, `year=2006`, `grade=NULL`

## Files

- `db.py`: MySQL connection using environment variables
- `functions.py`: Core database logic
- `gui.py`: Tkinter interface
- `main.py`: Entry point for GUI and CLI

## Verification

The Python files were checked with:

```bash
python3 -m py_compile db.py functions.py gui.py main.py
```
