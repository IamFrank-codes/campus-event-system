"""
schemas.py
Defines the request/response shapes for the Event API.
"""

from pydantic import BaseModel, Field
from datetime import datetime


class EventCreate(BaseModel):
    """Shape of data required to create a new event."""
    title: str = Field(..., min_length=3, max_length=150)
    description: str | None = None
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=150)
    event_date: datetime
    capacity: int = Field(..., gt=0)
    organizer_id: int


class EventUpdate(BaseModel):
    """Shape of data allowed when updating an event. All fields optional."""
    title: str | None = Field(None, min_length=3, max_length=150)
    description: str | None = None
    category: str | None = None
    location: str | None = None
    event_date: datetime | None = None
    capacity: int | None = Field(None, gt=0)


class EventResponse(BaseModel):
    """Shape of data sent back to the client."""
    id: int
    title: str
    description: str | None
    category: str
    location: str
    event_date: datetime
    capacity: int
    organizer_id: int
    created_at: datetime

    class Config:
        from_attributes = True