"""Tests for the Event Service with authenticated protected requests."""
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import main as main_module

engine = create_engine("sqlite:///./test_events.db", connect_args={"check_same_thread": False})
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

def auth_header(user_id=1, role="organizer"):
    token = jwt.encode({"sub": str(user_id), "role": role}, "dev-only-secret-change-this-in-production", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

VALID_EVENT = {
    "title": "AI Career Fair", "description": "Meet companies hiring in tech", "category": "career",
    "location": "Main Hall", "event_date": "2026-09-15T10:00:00", "capacity": 100, "organizer_id": 1,
}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_event_with_valid_organizer_succeeds(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    response = client.post("/api/events", headers=auth_header(), json=VALID_EVENT)
    assert response.status_code == 201
    assert response.json()["organizer_id"] == 1

def test_create_event_with_invalid_organizer_fails(monkeypatch):
    from fastapi import HTTPException, status
    def fake_verify(organizer_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")
    monkeypatch.setattr(main_module, "verify_organizer", fake_verify)
    response = client.post("/api/events", headers=auth_header(), json=VALID_EVENT)
    assert response.status_code == 400

def test_create_event_with_invalid_capacity_fails_validation(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    response = client.post("/api/events", headers=auth_header(), json={**VALID_EVENT, "capacity": 0})
    assert response.status_code == 422

def test_list_events_returns_created_events(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    client.post("/api/events", headers=auth_header(), json=VALID_EVENT)
    response = client.get("/api/events")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_list_events_filtered_by_category(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    client.post("/api/events", headers=auth_header(), json=VALID_EVENT)
    client.post("/api/events", headers=auth_header(), json={**VALID_EVENT, "category": "sports", "title": "Sports Day"})
    response = client.get("/api/events?category=career")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "career"

def test_get_nonexistent_event_returns_404():
    assert client.get("/api/events/9999").status_code == 404

def test_update_event_changes_only_given_fields(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    created = client.post("/api/events", headers=auth_header(), json=VALID_EVENT).json()
    response = client.put(f"/api/events/{created['id']}", headers=auth_header(), json={"capacity": 200})
    assert response.status_code == 200
    assert response.json()["capacity"] == 200
    assert response.json()["title"] == VALID_EVENT["title"]

def test_delete_event_removes_it(monkeypatch):
    monkeypatch.setattr(main_module, "verify_organizer", lambda organizer_id: None)
    created = client.post("/api/events", headers=auth_header(), json=VALID_EVENT).json()
    assert client.delete(f"/api/events/{created['id']}", headers=auth_header()).status_code == 204
    assert client.get(f"/api/events/{created['id']}").status_code == 404
