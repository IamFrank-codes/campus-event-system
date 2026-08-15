"""
schemas.py
Defines the request/response shapes for the Booking API.
"""

from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingCreate(BaseModel):
    """Shape of data required to create a booking."""
    event_id: int
    student_id: int


class BookingResponse(BaseModel):
    """Shape of data sent back to the client."""
    id: int
    event_id: int
    student_id: int
    status: BookingStatus
    booked_at: datetime

    class Config:
        from_attributes = True