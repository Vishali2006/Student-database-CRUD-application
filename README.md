# Students Database CRUD Application

A beginner-friendly REST API for managing student records. The application uses
FastAPI for HTTP endpoints and interactive API documentation, Pydantic for
validation, and Python's built-in `sqlite3` module for persistent storage.

## Features

- Create, list, retrieve, update, and delete student records.
- Automatically generated student IDs.
- Optional course filter when listing students.
- Validates email addresses, phone numbers, and dates of birth.
- Requires at least one contact method: email or phone.
- Prevents duplicate email addresses and returns a helpful conflict response.
- Uses parameterized SQL statements.
- Creates the SQLite database and table automatically at startup.
- Includes automated tests that use a separate temporary database.

## Technologies

- Python 3.10 or newer
- FastAPI
- Pydantic
- SQLite via Python's built-in `sqlite3`
- Uvicorn
- pytest and FastAPI TestClient

## Prerequisites

Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
On Windows, enable **Add Python to PATH** during installation. Verify the
installation in a new VS Code terminal:

```powershell
py --version
```

## Installation on Windows

Open this project folder (`student_crud_app`) in VS Code, then open a PowerShell
terminal in that folder.

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

Start the development server from the `student_crud_app` folder:

```powershell
python -m uvicorn main:app --reload
```

The API will be available at <http://127.0.0.1:8000>. Open
<http://127.0.0.1:8000/docs> for Swagger UI, where you can try each endpoint.
FastAPI also generates the OpenAPI schema at <http://127.0.0.1:8000/openapi.json>.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/students` | Register a student; returns `201 Created` |
| `GET` | `/students` | List students |
| `GET` | `/students?course=Computer%20Science` | Filter students by course |
| `GET` | `/students/{student_id}` | Get one student |
| `PUT` | `/students/{student_id}` | Replace all editable fields for a student |
| `DELETE` | `/students/{student_id}` | Delete a student; returns `204 No Content` |

Missing student IDs return `404 Not Found`; duplicate email addresses return
`409 Conflict`; invalid request data returns `422 Unprocessable Entity`.

## Example requests

Create a student with `POST /students`:

```json
{
  "name": "Alex Example",
  "date_of_birth": "2002-04-15",
  "email": "alex@example.com",
  "phone": "+1 (555) 010-1234",
  "course": "Computer Science",
  "address": "123 Example Street",
  "enrollment_date": "2024-09-01"
}
```

At least one of `email` and `phone` must be provided. Optional fields may be
omitted or set to `null`. The `PUT` endpoint accepts the same complete set of
fields as the create endpoint.

Example `curl` request from PowerShell:

```powershell
curl.exe -X POST http://127.0.0.1:8000/students `
  -H "Content-Type: application/json" `
  -d '{"name":"Alex Example","date_of_birth":"2002-04-15","email":"alex@example.com","course":"Computer Science"}'
```

## Run tests

Install the requirements above, then run from the project folder:

```powershell
python -m pytest
```

Each test creates its own database under pytest's temporary directory. Running
tests does not read or modify the application database.

## Database persistence

On the first application startup, SQLite creates `students.db` beside
`main.py`. The database file is ignored by Git. The data remains in that file
after the server stops and is available the next time the application starts.
Tests pass a temporary database path to the application factory instead.

## Project structure

```text
student_crud_app/
├── main.py             # FastAPI application and endpoint definitions
├── database.py         # SQLite setup and parameterized database operations
├── schemas.py          # Pydantic request and response validation
├── requirements.txt    # Application and test dependencies
├── README.md           # Setup and API guide
├── .gitignore          # Excludes local databases and environment files
└── tests/
    └── test_main.py    # Automated API tests using a temporary database
```
