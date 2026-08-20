"""
schemas.py
Defines the request/response shapes for the Event API.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum

class EventCategory(str, Enum):
    CAREER = "career"
    SPORTS = "sports"
    ACADEMIC = "academic"
    SOCIAL = "social"
    WORKSHOP = "workshop"
    OTHER = "other"
    
class EventCreate(BaseModel):
    """Shape of data required to create a new event."""
    title: str = Field(..., min_length=3, max_length=150)
    description: str | None = None
    category: EventCategory
    location: str = Field(..., min_length=2, max_length=150)
    event_date: datetime
    capacity: int = Field(..., gt=0)
    organizer_id: int


class EventUpdate(BaseModel):
    """Shape of data allowed when updating an event. All fields optional."""
    title: str | None = Field(None, min_length=3, max_length=150)
    description: str | None = None
    category: EventCategory | None = None
    location: str | None = None
    event_date: datetime | None = None
    capacity: int | None = Field(None, gt=0)


class EventResponse(BaseModel):
    """Shape of data sent back to the client."""
    id: int
    title: str
    description: str | None
    category: EventCategory
    location: str
    event_date: datetime
    capacity: int
    organizer_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



