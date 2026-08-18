"""
test_main.py
Unit tests for the Booking Service.
Mocks both the User service and Event service calls, so these tests
run completely independently, without needing either service live.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
import main as main_module

TEST_DATABASE_URL = "sqlite:///./test_bookings.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

FAKE_EVENT = {
    "id": 1,
    "title": "AI Career Fair",
    "capacity": 2,  # deliberately small, to test the "fully booked" case easily
    "organizer_id": 5,
}


def mock_all_services_valid(monkeypatch, event_data=None):
    """Fakes both external services responding successfully."""
    monkeypatch.setattr(main_module, "verify_student", lambda student_id: None)
    monkeypatch.setattr(
        main_module, "get_event_or_error", lambda event_id: event_data or FAKE_EVENT
    )


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_booking_succeeds_when_everything_valid(monkeypatch):
    mock_all_services_valid(monkeypatch)

    response = client.post("/api/bookings", json={"event_id": 1, "student_id": 10})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["student_id"] == 10


def test_create_booking_fails_when_student_invalid(monkeypatch):
    from fastapi import HTTPException, status

    def fake_verify_student(student_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")

    monkeypatch.setattr(main_module, "verify_student", fake_verify_student)
    monkeypatch.setattr(main_module, "get_event_or_error", lambda event_id: FAKE_EVENT)

    response = client.post("/api/bookings", json={"event_id": 1, "student_id": 999})
    assert response.status_code == 400


def test_create_booking_fails_when_event_invalid(monkeypatch):
    from fastapi import HTTPException, status

    def fake_get_event(event_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No event found")

    monkeypatch.setattr(main_module, "verify_student", lambda student_id: None)
    monkeypatch.setattr(main_module, "get_event_or_error", fake_get_event)

    response = client.post("/api/bookings", json={"event_id": 999, "student_id": 10})
    assert response.status_code == 400


def test_duplicate_booking_by_same_student_fails(monkeypatch):
    mock_all_services_valid(monkeypatch)

    client.post("/api/bookings", json={"event_id": 1, "student_id": 10})
    response = client.post("/api/bookings", json={"event_id": 1, "student_id": 10})
    assert response.status_code == 409
    assert "already has a booking" in response.json()["detail"]


def test_booking_fails_when_event_is_full(monkeypatch):
    """FAKE_EVENT has capacity=2, so a 3rd different student should be rejected."""
    mock_all_services_valid(monkeypatch)

    client.post("/api/bookings", json={"event_id": 1, "student_id": 1})
    client.post("/api/bookings", json={"event_id": 1, "student_id": 2})
    response = client.post("/api/bookings", json={"event_id": 1, "student_id": 3})

    assert response.status_code == 409
    assert "fully booked" in response.json()["detail"]


def test_get_student_bookings_returns_their_bookings(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", json={"event_id": 1, "student_id": 10})

    response = client.get("/api/bookings/student/10")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_event_bookings_returns_attendees(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", json={"event_id": 1, "student_id": 10})
    client.post("/api/bookings", json={"event_id": 1, "student_id": 20})

    response = client.get("/api/bookings/event/1")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_cancel_booking_frees_up_the_spot(monkeypatch):
    """After cancelling, a new student should be able to book the freed spot."""
    mock_all_services_valid(monkeypatch)

    client.post("/api/bookings", json={"event_id": 1, "student_id": 1})
    booking2 = client.post("/api/bookings", json={"event_id": 1, "student_id": 2}).json()

    # Capacity is 2, so it's now full - cancel one to free a spot
    cancel_response = client.delete(f"/api/bookings/{booking2['id']}")
    assert cancel_response.status_code == 204

    # Now a third student should be able to book successfully
    response = client.post("/api/bookings", json={"event_id": 1, "student_id": 3})
    assert response.status_code == 201


def test_cancel_nonexistent_booking_returns_404():
    response = client.delete("/api/bookings/9999")
    assert response.status_code == 404