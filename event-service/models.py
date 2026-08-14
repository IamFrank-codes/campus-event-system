"""
models.py
Defines the Event table structure.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False)
    # organizer_id refers to a user in the User service's database -
    # this service doesn't store user details itself, just their id
    organizer_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())