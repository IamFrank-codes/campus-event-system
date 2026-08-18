"""
main.py
Review Service - Campus Event Management System

Lets students leave a rating and comment for an event after attending.
Also calculates an average rating per event - useful for organizers
and other students browsing events.

Run with:
    uvicorn main:app --reload --port 8005
Then visit http://127.0.0.1:8005/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from database import Base, engine, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Review Service",
    description="Handles event reviews for the Campus Event Management System",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "review-service"}


@app.post("/api/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(review_in: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """Creates a new review. A student can only review a given event once."""
    existing = db.query(models.Review).filter(
        models.Review.event_id == review_in.event_id,
        models.Review.student_id == review_in.student_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student has already reviewed this event",
        )

    new_review = models.Review(**review_in.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@app.get("/api/reviews/event/{event_id}", response_model=list[schemas.ReviewResponse])
def get_event_reviews(event_id: int, db: Session = Depends(get_db)):
    """Lists all reviews left for a specific event."""
    return db.query(models.Review).filter(models.Review.event_id == event_id).all()


@app.get("/api/reviews/event/{event_id}/average")
def get_event_average_rating(event_id: int, db: Session = Depends(get_db)):
    """Returns the average rating for an event, and how many reviews it's based on."""
    result = db.query(
        sql_func.avg(models.Review.rating),
        sql_func.count(models.Review.id),
    ).filter(models.Review.event_id == event_id).first()

    average, count = result
    if count == 0:
        return {"event_id": event_id, "average_rating": None, "review_count": 0}

    return {
        "event_id": event_id,
        "average_rating": round(average, 2),
        "review_count": count,
    }


@app.delete("/api/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Deletes a review."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    db.delete(review)
    db.commit()
