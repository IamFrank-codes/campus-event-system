"""
test_main.py
Unit tests for the Event Service.
Uses monkeypatching to fake responses from the User service, so these
tests never actually need the User service running.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
import main as main_module

TEST_DATABASE_URL = "sqlite:///./test_events.db"
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

VALID_EVENT = {
    "title": "AI Career Fair",
    "description": "Meet companies hiring in tech",
    "category": "career",
    "location": "Main Hall",
    "event_date": "2026-09-15T10:00:00",
    "capacity": 100,
    "organizer_id": 1,
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_event_with_valid_organizer_succeeds(monkeypatch):
    """
    Fakes a successful response from the User service, as if organizer_id=1
    is a real organizer - without actually calling the real service.
    """
    def fake_verify_organizer(organizer_id):
        return None  # simulates: organizer is valid, no error raised

    monkeypatch.setattr(main_module, "verify_organizer", fake_verify_organizer)

    response = client.post("/api/events", json=VALID_EVENT)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "AI Career Fair"
    assert data["organizer_id"] == 1


def test_create_event_with_invalid_organizer_fails(monkeypatch):
    """
    Fakes the User service saying 'this organizer doesn't exist',
    and checks the Event service correctly refuses to create the event.
    """
    from fastapi import HTTPException, status

    def fake_verify_organizer(organizer_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")

    monkeypatch.setattr(main_module, "verify_organizer", fake_verify_organizer)

    response = client.post("/api/events", json=VALID_EVENT)
    assert response.status_code == 400


def test_create_event_with_invalid_capacity_fails_validation(monkeypatch):
    """Capacity of 0 or below should be rejected before even checking the organizer."""
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)

    bad_event = VALID_EVENT.copy()
    bad_event["capacity"] = 0

    response = client.post("/api/events", json=bad_event)
    assert response.status_code == 422


def test_list_events_returns_created_events(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    client.post("/api/events", json=VALID_EVENT)

    response = client.get("/api/events")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_events_filtered_by_category(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    client.post("/api/events", json=VALID_EVENT)

    other_event = VALID_EVENT.copy()
    other_event["category"] = "sports"
    client.post("/api/events", json=other_event)

    response = client.get("/api/events?category=career")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["category"] == "career"


def test_get_nonexistent_event_returns_404():
    response = client.get("/api/events/9999")
    assert response.status_code == 404


def test_update_event_changes_only_given_fields(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    created = client.post("/api/events", json=VALID_EVENT).json()

    response = client.put(f"/api/events/{created['id']}", json={"capacity": 200})
    assert response.status_code == 200
    data = response.json()
    assert data["capacity"] == 200
    assert data["title"] == VALID_EVENT["title"]  # unchanged


def test_delete_event_removes_it(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    created = client.post("/api/events", json=VALID_EVENT).json()

    delete_response = client.delete(f"/api/events/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/events/{created['id']}")
    assert get_response.status_code == 404