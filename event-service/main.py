"""
main.py
Event Service - Campus Event Management System

Handles creating, listing, updating, and deleting events.
This service does NOT store user data itself - whenever it needs to
check that an organizer is real, it calls the User/Auth service over HTTP.
This is what makes it a genuine service-oriented system, not just
separate apps sitting next to each other.

Run with:
    uvicorn main:app --reload --port 8002
Then visit http://127.0.0.1:8002/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx

from database import Base, engine, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Service",
    description="Handles campus events for the Campus Event Management System",
    version="1.0.0",
)

# The address of the User service - in a real deployment this would come
# from an environment variable, not be hardcoded
USER_SERVICE_URL = "http://127.0.0.1:8001"


def verify_organizer(organizer_id: int):
    """
    Calls the User service to check the organizer actually exists.
    This is a real network call to a DIFFERENT running service -
    the core of service-oriented design.
    """
    try:
        response = httpx.get(f"{USER_SERVICE_URL}/api/users/{organizer_id}", timeout=5.0)
    except httpx.ConnectError:
        # The User service isn't running or isn't reachable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service is unavailable - cannot verify organizer",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No user found with id {organizer_id}",
        )

    user_data = response.json()
    if user_data.get("role") not in ("organizer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizers or admins can create events",
        )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "event-service"}


@app.post("/api/events", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    """Creates a new event, after checking the organizer is a real, valid user."""
    verify_organizer(event_in.organizer_id)

    new_event = models.Event(**event_in.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.get("/api/events", response_model=list[schemas.EventResponse])
def list_events(category: str | None = None, db: Session = Depends(get_db)):
    """Lists all events, optionally filtered by category."""
    query = db.query(models.Event)
    if category:
        query = query.filter(models.Event.category == category)
    return query.all()


@app.get("/api/events/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Gets a single event by id."""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@app.put("/api/events/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, updates: schemas.EventUpdate, db: Session = Depends(get_db)):
    """Updates an existing event's details."""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@app.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Deletes an event."""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()