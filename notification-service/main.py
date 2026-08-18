"""
main.py
Booking Service - Campus Event Management System

Handles students booking spots at events. Before confirming a booking,
this service checks TWO other services:
1. User service - is this a real, registered student?
2. Event service - does this event exist, and is there still room?

This is the clearest example in the whole system of services
genuinely depending on and coordinating with each other.

Run with:
    uvicorn main:app --reload --port 8003
Then visit http://127.0.0.1:8003/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx

from database import Base, engine, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Booking Service",
    description="Handles event bookings for the Campus Event Management System",
    version="1.0.0",
)

USER_SERVICE_URL = "http://127.0.0.1:8001"
EVENT_SERVICE_URL = "http://127.0.0.1:8002"


def verify_student(student_id: int):
    """Checks the User service that this student actually exists."""
    try:
        response = httpx.get(f"{USER_SERVICE_URL}/api/users/{student_id}", timeout=5.0)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service is unavailable - cannot verify student",
        )
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No user found with id {student_id}",
        )


def get_event_or_error(event_id: int) -> dict:
    """Checks the Event service that this event actually exists, and returns its data."""
    try:
        response = httpx.get(f"{EVENT_SERVICE_URL}/api/events/{event_id}", timeout=5.0)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event service is unavailable - cannot verify event",
        )
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No event found with id {event_id}",
        )
    return response.json()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "booking-service"}


@app.post("/api/bookings", response_model=schemas.BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: schemas.BookingCreate, db: Session = Depends(get_db)):
    """
    Books a student into an event, after checking:
    - the student is real (User service)
    - the event is real (Event service)
    - the event isn't already full (counted from this service's own bookings)
    """
    verify_student(booking_in.student_id)
    event = get_event_or_error(booking_in.event_id)

    existing_bookings = db.query(models.Booking).filter(
        models.Booking.event_id == booking_in.event_id,
        models.Booking.status == "confirmed",
    ).count()

    if existing_bookings >= event["capacity"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This event is already fully booked",
        )

    already_booked = db.query(models.Booking).filter(
        models.Booking.event_id == booking_in.event_id,
        models.Booking.student_id == booking_in.student_id,
        models.Booking.status == "confirmed",
    ).first()

    if already_booked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student already has a booking for this event",
        )

    new_booking = models.Booking(
        event_id=booking_in.event_id,
        student_id=booking_in.student_id,
        status="confirmed",
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@app.get("/api/bookings/student/{student_id}", response_model=list[schemas.BookingResponse])
def get_student_bookings(student_id: int, db: Session = Depends(get_db)):
    """Lists all bookings made by a specific student."""
    return db.query(models.Booking).filter(models.Booking.student_id == student_id).all()


@app.get("/api/bookings/event/{event_id}", response_model=list[schemas.BookingResponse])
def get_event_bookings(event_id: int, db: Session = Depends(get_db)):
    """Lists all bookings for a specific event - useful for an organizer to see who's coming."""
    return db.query(models.Booking).filter(models.Booking.event_id == event_id).all()


@app.delete("/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancels a booking, freeing up the spot for someone else."""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking.status = "cancelled"
    db.commit()