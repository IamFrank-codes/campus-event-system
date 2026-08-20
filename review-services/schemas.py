"""
schemas.py
Defines the request/response shapes for the Review API.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ReviewCreate(BaseModel):
    """Shape of data required to leave a review."""
    event_id: int
    student_id: int
    rating: int = Field(..., ge=1, le=5)  # ge = greater/equal, le = less/equal
    comment: str | None = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Shape of data sent back to the client."""
    id: int
    event_id: int
    student_id: int
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
