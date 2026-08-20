"""Tests for the Notification Service."""
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test_notifications.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth_header(user_id=10, role="student"):
    token = jwt.encode({"sub": str(user_id), "role": role}, "dev-only-secret-change-this-in-production", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def fake_get(url, timeout=5.0):
    class Response:
        status_code = 200
    return Response()

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("main.httpx.get", fake_get)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "notification-service"


def test_send_notification_succeeds():
    response = client.post("/api/notifications/send", headers=auth_header(), json={
        "user_id": 10, "event_id": 1, "notification_type": "booking_confirmation", "message": "Booking confirmed"
    })
    assert response.status_code == 201
    assert response.json()["is_read"] is False
    assert response.json()["notification_type"] == "booking_confirmation"


def test_user_cannot_send_for_another_user():
    response = client.post("/api/notifications/send", headers=auth_header(10), json={
        "user_id": 20, "message": "Not allowed"
    })
    assert response.status_code == 403


def test_list_and_mark_notification_read():
    created = client.post("/api/notifications/send", headers=auth_header(), json={
        "user_id": 10, "message": "Reminder"
    }).json()
    listed = client.get("/api/notifications/user/10", headers=auth_header()).json()
    assert len(listed) == 1
    updated = client.patch(f"/api/notifications/{created['id']}/read", headers=auth_header())
    assert updated.status_code == 200
    assert updated.json()["is_read"] is True


def test_invalid_notification_type_fails_validation():
    response = client.post("/api/notifications/send", headers=auth_header(), json={
        "user_id": 10, "notification_type": "invalid", "message": "Test"
    })
    assert response.status_code == 422


def test_unverified_user_returns_404(monkeypatch):
    class Missing:
        status_code = 404
    monkeypatch.setattr("main.httpx.get", lambda *args, **kwargs: Missing())
    response = client.post("/api/notifications/send", headers=auth_header(), json={
        "user_id": 10, "message": "Test"
    })
    assert response.status_code == 404
