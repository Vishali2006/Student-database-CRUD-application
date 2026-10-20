"""FastAPI application for managing student records."""

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Response, status

import database
from schemas import StudentCreate, StudentResponse, StudentUpdate


def create_app(database_path: Path = database.DATABASE_PATH) -> FastAPI:
    """Create the API application, optionally using a separate SQLite file."""

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        database.initialize_database(database_path)
        yield

    app = FastAPI(
        title="Students Database CRUD Application",
        description="A simple API for creating and managing student records.",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.post(
        "/students",
        response_model=StudentResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Register a student",
    )
    def create_student(student: StudentCreate) -> dict:
        """Create a student record and return its generated ID."""
        try:
            return database.create_student(database_path, student)
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with this email address already exists.",
            ) from error

    @app.get(
        "/students",
        response_model=list[StudentResponse],
        summary="List students",
    )
    def list_students(
        course: str | None = Query(
            default=None, min_length=1, max_length=100, description="Filter by course"
        ),
    ) -> list[dict]:
        """Return all students, optionally filtered by course."""
        return database.list_students(database_path, course)

    @app.get(
        "/students/{student_id}",
        response_model=StudentResponse,
        summary="Get a student",
    )
    def get_student(student_id: int) -> dict:
        """Return one student, or 404 if the ID does not exist."""
        student = database.get_student(database_path, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
            )
        return student

    @app.put(
        "/students/{student_id}",
        response_model=StudentResponse,
        summary="Replace a student",
    )
    def update_student(student_id: int, student: StudentUpdate) -> dict:
        """Replace an existing student's details without creating a record."""
        try:
            updated_student = database.update_student(
                database_path, student_id, student
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with this email address already exists.",
            ) from error
        if updated_student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
            )
        return updated_student

    @app.delete(
        "/students/{student_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a student",
    )
    def delete_student(student_id: int) -> Response:
        """Delete a student, or return 404 if the ID does not exist."""
        if not database.delete_student(database_path, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
