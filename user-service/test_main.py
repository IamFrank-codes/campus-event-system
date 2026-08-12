"""
test_main.py
Unit tests for the User/Auth service, using pytest + FastAPI's TestClient.
Run with:
    pytest -v

Uses a separate in-memory SQLite database so tests never touch users.db.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# --- Test database setup (isolated from the real users.db) ---
TEST_DATABASE_URL = "sqlite:///./test_users.db"
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
    """Creates fresh tables before each test and drops them after, so tests don't affect each other."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health_check():
    """The service should report itself as healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_new_user_succeeds():
    """A valid registration should return 201 and the new user's data (without the password)."""
    response = client.post("/api/auth/register", json={
        "full_name": "Thabo Mokoena",
        "email": "thabo@example.com",
        "password": "securepass123",
        "role": "student",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "thabo@example.com"
    assert "hashed_password" not in data  # password must never be returned


def test_register_duplicate_email_fails():
    """Registering the same email twice should fail with 409 Conflict, not crash."""
    payload = {
        "full_name": "Lerato Dube",
        "email": "lerato@example.com",
        "password": "securepass123",
        "role": "organizer",
    }
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"]


def test_register_with_short_password_fails_validation():
    """Passwords under 6 characters should be rejected before ever reaching the database."""
    response = client.post("/api/auth/register", json={
        "full_name": "Sipho Nkosi",
        "email": "sipho@example.com",
        "password": "123",
        "role": "student",
    })
    assert response.status_code == 422  # FastAPI's automatic validation error


def test_login_with_correct_credentials_returns_token():
    """A correct email/password should return a usable JWT access token."""
    client.post("/api/auth/register", json={
        "full_name": "Naledi Van Wyk",
        "email": "naledi@example.com",
        "password": "correctpass1",
        "role": "student",
    })

    response = client.post("/api/auth/login", json={
        "email": "naledi@example.com",
        "password": "correctpass1",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_fails():
    """Login should fail with 401 for a wrong password, and never reveal whether the email exists."""
    client.post("/api/auth/register", json={
        "full_name": "Kagiso Pillay",
        "email": "kagiso@example.com",
        "password": "correctpass1",
        "role": "student",
    })

    response = client.post("/api/auth/login", json={
        "email": "kagiso@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_protected_route_without_token_fails():
    """Accessing /api/users/me without a token should be rejected."""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_protected_route_with_valid_token_succeeds():
    """A valid token should grant access to the user's own profile."""
    client.post("/api/auth/register", json={
        "full_name": "Zanele Botha",
        "email": "zanele@example.com",
        "password": "correctpass1",
        "role": "student",
    })
    login_response = client.post("/api/auth/login", json={
        "email": "zanele@example.com",
        "password": "correctpass1",
    })
    token = login_response.json()["access_token"]

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "zanele@example.com"


def test_get_nonexistent_user_returns_404():
    """Looking up a user id that doesn't exist should return a clean 404, not a server error."""
    response = client.get("/api/users/9999")
    assert response.status_code == 404