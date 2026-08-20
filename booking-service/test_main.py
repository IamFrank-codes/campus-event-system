"""Tests for the Booking Service with authenticated protected requests."""
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import main as main_module

engine = create_engine("sqlite:///./test_bookings.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def auth_header(user_id=10, role="student"):
    token = jwt.encode({"sub": str(user_id), "role": role}, "dev-only-secret-change-this-in-production", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

def mock_all_services_valid(monkeypatch, event_data=None):
    monkeypatch.setattr(main_module, "verify_student", lambda student_id: None)
    monkeypatch.setattr(main_module, "get_event_or_error", lambda event_id: event_data or {"id": 1, "capacity": 2})

def book(student_id=10):
    return {"event_id": 1, "student_id": student_id}

def test_health_check():
    assert client.get("/health").status_code == 200

def test_create_booking_succeeds_when_everything_valid(monkeypatch):
    mock_all_services_valid(monkeypatch)
    response = client.post("/api/bookings", headers=auth_header(10), json=book(10))
    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"

def test_create_booking_fails_when_student_invalid(monkeypatch):
    from fastapi import HTTPException, status
    def fake_verify(student_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")
    monkeypatch.setattr(main_module, "verify_student", fake_verify)
    monkeypatch.setattr(main_module, "get_event_or_error", lambda event_id: {"id": 1, "capacity": 2})
    response = client.post("/api/bookings", headers=auth_header(999), json=book(999))
    assert response.status_code == 400

def test_create_booking_fails_when_event_invalid(monkeypatch):
    from fastapi import HTTPException, status
    def fake_get_event(event_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No event found")
    monkeypatch.setattr(main_module, "verify_student", lambda student_id: None)
    monkeypatch.setattr(main_module, "get_event_or_error", fake_get_event)
    response = client.post("/api/bookings", headers=auth_header(10), json=book(10))
    assert response.status_code == 400

def test_duplicate_booking_by_same_student_fails(monkeypatch):
    mock_all_services_valid(monkeypatch)
    headers = auth_header(10)
    client.post("/api/bookings", headers=headers, json=book(10))
    response = client.post("/api/bookings", headers=headers, json=book(10))
    assert response.status_code == 409

def test_booking_fails_when_event_is_full(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", headers=auth_header(1), json=book(1))
    client.post("/api/bookings", headers=auth_header(2), json=book(2))
    response = client.post("/api/bookings", headers=auth_header(3), json=book(3))
    assert response.status_code == 409

def test_get_student_bookings_returns_their_bookings(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", headers=auth_header(10), json=book(10))
    response = client.get("/api/bookings/student/10", headers=auth_header(10))
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_event_bookings_returns_attendees(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", headers=auth_header(10), json=book(10))
    client.post("/api/bookings", headers=auth_header(20), json=book(20))
    response = client.get("/api/bookings/event/1", headers=auth_header(5, "organizer"))
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_cancel_booking_frees_up_the_spot(monkeypatch):
    mock_all_services_valid(monkeypatch)
    client.post("/api/bookings", headers=auth_header(1), json=book(1))
    booking2 = client.post("/api/bookings", headers=auth_header(2), json=book(2)).json()
    assert client.delete(f"/api/bookings/{booking2['id']}", headers=auth_header(2)).status_code == 204
    assert client.post("/api/bookings", headers=auth_header(3), json=book(3)).status_code == 201

def test_cancel_nonexistent_booking_returns_404():
    assert client.delete("/api/bookings/9999", headers=auth_header(10)).status_code == 404
