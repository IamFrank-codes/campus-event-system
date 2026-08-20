"""Tests for the Review Service with authenticated protected requests."""
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

engine = create_engine("sqlite:///./test_reviews.db", connect_args={"check_same_thread": False})
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

def review(student_id=10, rating=5, event_id=1):
    return {"event_id": event_id, "student_id": student_id, "rating": rating, "comment": "Good event"}

def test_health_check():
    assert client.get("/health").status_code == 200

def test_create_review_succeeds():
    response = client.post("/api/reviews", headers=auth_header(10), json=review())
    assert response.status_code == 201
    assert response.json()["rating"] == 5

def test_create_review_with_rating_above_5_fails_validation():
    response = client.post("/api/reviews", headers=auth_header(10), json=review(rating=6))
    assert response.status_code == 422

def test_create_review_with_rating_below_1_fails_validation():
    response = client.post("/api/reviews", headers=auth_header(10), json=review(rating=0))
    assert response.status_code == 422

def test_duplicate_review_by_same_student_fails():
    payload = review(rating=4)
    assert client.post("/api/reviews", headers=auth_header(10), json=payload).status_code == 201
    second = client.post("/api/reviews", headers=auth_header(10), json=payload)
    assert second.status_code == 409
    assert "already reviewed" in second.json()["detail"]

def test_get_event_reviews_returns_all_reviews_for_that_event():
    client.post("/api/reviews", headers=auth_header(10), json=review(10, 5, 1))
    client.post("/api/reviews", headers=auth_header(20), json=review(20, 3, 1))
    client.post("/api/reviews", headers=auth_header(10), json=review(10, 4, 2))
    response = client.get("/api/reviews/event/1")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_average_rating_calculates_correctly():
    client.post("/api/reviews", headers=auth_header(10), json=review(10, 5, 1))
    client.post("/api/reviews", headers=auth_header(20), json=review(20, 3, 1))
    response = client.get("/api/reviews/event/1/average")
    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.0
    assert response.json()["review_count"] == 2

def test_average_rating_with_no_reviews_returns_none():
    response = client.get("/api/reviews/event/999/average")
    assert response.status_code == 200
    assert response.json()["average_rating"] is None
    assert response.json()["review_count"] == 0

def test_delete_review_removes_it():
    created = client.post("/api/reviews", headers=auth_header(10), json=review()).json()
    assert client.delete(f"/api/reviews/{created['id']}", headers=auth_header(10)).status_code == 204
    assert len(client.get("/api/reviews/event/1").json()) == 0

def test_delete_nonexistent_review_returns_404():
    assert client.delete("/api/reviews/9999", headers=auth_header(10)).status_code == 404
