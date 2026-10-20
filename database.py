"""SQLite database setup and student record operations."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from schemas import StudentCreate, StudentUpdate

DATABASE_PATH = Path(__file__).resolve().parent / "students.db"


@contextmanager
def get_connection(database_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    """Open a database connection and close it after the operation."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    """Create the student table when it does not already exist."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                date_of_birth TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT,
                CHECK (email IS NOT NULL OR phone IS NOT NULL)
            )
            """
        )


def _student_values(student: StudentCreate | StudentUpdate) -> tuple:
    values = student.model_dump(mode="json")
    return (
        values["name"],
        values["date_of_birth"],
        str(values["email"]) if values["email"] is not None else None,
        values["phone"],
        values["course"],
        values["address"],
        values["enrollment_date"],
    )


def _row_to_student(row: sqlite3.Row) -> dict:
    return dict(row)


def create_student(database_path: Path, student: StudentCreate) -> dict:
    """Insert a student and return the stored record."""
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO students (
                name, date_of_birth, email, phone, course, address, enrollment_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _student_values(student),
        )
        row = connection.execute(
            "SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _row_to_student(row)


def list_students(database_path: Path, course: str | None = None) -> list[dict]:
    """Return all students, optionally filtering by course."""
    with get_connection(database_path) as connection:
        if course is None:
            rows = connection.execute(
                "SELECT * FROM students ORDER BY id"
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM students WHERE course = ? COLLATE NOCASE ORDER BY id",
                (course,),
            ).fetchall()
    return [_row_to_student(row) for row in rows]


def get_student(database_path: Path, student_id: int) -> dict | None:
    """Return one student by ID, or None when no record matches."""
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    return _row_to_student(row) if row is not None else None


def update_student(
    database_path: Path, student_id: int, student: StudentUpdate
) -> dict | None:
    """Replace a student's editable fields without creating a new record."""
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE students
            SET name = ?, date_of_birth = ?, email = ?, phone = ?,
                course = ?, address = ?, enrollment_date = ?
            WHERE id = ?
            """,
            (*_student_values(student), student_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    return _row_to_student(row)


def delete_student(database_path: Path, student_id: int) -> bool:
    """Delete a student and report whether a record was removed."""
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE id = ?", (student_id,)
        )
    return cursor.rowcount > 0
