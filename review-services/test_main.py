"""
test_main.py
Unit tests for the Review Service.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test_reviews.db"
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


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_review_succeeds():
    response = client.post("/api/reviews", json={
        "event_id": 1,
        "student_id": 10,
        "rating": 5,
        "comment": "Loved this event!",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5


def test_create_review_with_rating_above_5_fails_validation():
    response = client.post("/api/reviews", json={
        "event_id": 1,
        "student_id": 10,
        "rating": 6,
        "comment": "Too high",
    })
    assert response.status_code == 422


def test_create_review_with_rating_below_1_fails_validation():
    response = client.post("/api/reviews", json={
        "event_id": 1,
        "student_id": 10,
        "rating": 0,
        "comment": "Too low",
    })
    assert response.status_code == 422


def test_duplicate_review_by_same_student_fails():
    payload = {"event_id": 1, "student_id": 10, "rating": 4, "comment": "Good"}
    first = client.post("/api/reviews", json=payload)
    assert first.status_code == 201

    second = client.post("/api/reviews", json=payload)
    assert second.status_code == 409
    assert "already reviewed" in second.json()["detail"]


def test_get_event_reviews_returns_all_reviews_for_that_event():
    client.post("/api/reviews", json={"event_id": 1, "student_id": 10, "rating": 5})
    client.post("/api/reviews", json={"event_id": 1, "student_id": 20, "rating": 3})
    client.post("/api/reviews", json={"event_id": 2, "student_id": 10, "rating": 4})

    response = client.get("/api/reviews/event/1")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_average_rating_calculates_correctly():
    client.post("/api/reviews", json={"event_id": 1, "student_id": 10, "rating": 5})
    client.post("/api/reviews", json={"event_id": 1, "student_id": 20, "rating": 3})

    response = client.get("/api/reviews/event/1/average")
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.0
    assert data["review_count"] == 2


def test_average_rating_with_no_reviews_returns_none():
    response = client.get("/api/reviews/event/999/average")
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] is None
    assert data["review_count"] == 0


def test_delete_review_removes_it():
    created = client.post("/api/reviews", json={
        "event_id": 1, "student_id": 10, "rating": 5,
    }).json()

    delete_response = client.delete(f"/api/reviews/{created['id']}")
    assert delete_response.status_code == 204

    check = client.get("/api/reviews/event/1")
    assert len(check.json()) == 0


def test_delete_nonexistent_review_returns_404():
    response = client.delete("/api/reviews/9999")
    assert response.status_code == 404
