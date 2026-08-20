"""
schemas.py
Pydantic models define what data the API expects to receive (requests)
and what it promises to send back (responses). FastAPI uses these to
auto-validate incoming data and to auto-generate the /docs page.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal


class UserCreate(BaseModel):
    """Shape of data required to register a new user."""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["student", "organizer", "admin"] = "student"


class UserLogin(BaseModel):
    """Shape of data required to log in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Shape of data sent back to the client after registration or lookup.
    Notice hashed_password is NOT included here - never return password data.
    """
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read SQLAlchemy objects directly


class Token(BaseModel):
    """Shape of the response returned after a successful login."""
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    """Shape of data allowed when updating a user profile."""
    full_name: str | None = Field(None, min_length=2, max_length=100)
