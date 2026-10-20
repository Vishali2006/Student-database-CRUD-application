from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test_students.db")
    with TestClient(app) as test_client:
        yield test_client


def valid_student(**overrides):
    student = {
        "name": "Alex Example",
        "date_of_birth": "2002-04-15",
        "email": "alex@example.com",
        "phone": "+1 (555) 010-1234",
        "course": "Computer Science",
        "address": "123 Example Street",
        "enrollment_date": "2024-09-01",
    }
    student.update(overrides)
    return student


def test_create_student_returns_generated_id_and_details(client):
    response = client.post("/students", json=valid_student())

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Alex Example"
    assert response.json()["date_of_birth"] == "2002-04-15"


def test_list_students_and_filter_by_course(client):
    client.post("/students", json=valid_student())
    client.post(
        "/students",
        json=valid_student(
            name="Jordan Example",
            email="jordan@example.com",
            course="History",
        ),
    )

    assert len(client.get("/students").json()) == 2
    filtered = client.get("/students", params={"course": "computer science"})
    assert filtered.status_code == 200
    assert [student["name"] for student in filtered.json()] == ["Alex Example"]


def test_get_student_by_id(client):
    created = client.post("/students", json=valid_student()).json()

    response = client.get(f"/students/{created['id']}")

    assert response.status_code == 200
    assert response.json()["email"] == "alex@example.com"


def test_update_student_replaces_existing_record(client):
    created = client.post("/students", json=valid_student()).json()
    updated_data = valid_student(name="Alex Updated", email="updated@example.com")

    response = client.put(f"/students/{created['id']}", json=updated_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Alex Updated"
    assert len(client.get("/students").json()) == 1


def test_delete_student(client):
    created = client.post("/students", json=valid_student()).json()

    response = client.delete(f"/students/{created['id']}")

    assert response.status_code == 204
    assert client.get("/students").json() == []


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/students/999"),
        ("put", "/students/999"),
        ("delete", "/students/999"),
    ],
)
def test_nonexistent_student_returns_404(client, method, path):
    payload = valid_student() if method == "put" else None
    response = getattr(client, method)(path, json=payload) if payload else getattr(
        client, method
    )(path)

    assert response.status_code == 404


def test_invalid_email_is_rejected(client):
    response = client.post("/students", json=valid_student(email="not-an-email"))

    assert response.status_code == 422


def test_contact_method_is_required(client):
    response = client.post(
        "/students", json=valid_student(email=None, phone="   ")
    )

    assert response.status_code == 422


def test_blank_name_is_rejected_without_creating_a_record(client):
    response = client.post("/students", json=valid_student(name="   "))

    assert response.status_code == 422
    assert client.get("/students").json() == []


def test_future_date_of_birth_is_rejected(client):
    future_date = (date.today() + timedelta(days=1)).isoformat()

    response = client.post(
        "/students", json=valid_student(date_of_birth=future_date)
    )

    assert response.status_code == 422


def test_duplicate_email_is_rejected(client):
    client.post("/students", json=valid_student())

    response = client.post(
        "/students",
        json=valid_student(name="Another Student", phone=None),
    )

    assert response.status_code == 409


def test_student_data_persists_after_application_restart(tmp_path):
    database_path = tmp_path / "persistent_students.db"

    with TestClient(create_app(database_path)) as first_client:
        created = first_client.post("/students", json=valid_student())
        assert created.status_code == 201
        student_id = created.json()["id"]

    with TestClient(create_app(database_path)) as restarted_client:
        response = restarted_client.get(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Alex Example"
