"""
models.py
Defines the Booking table structure.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    # These reference records in OTHER services' databases -
    # this service just stores the ids, not the actual data
    event_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False, default="confirmed")  # confirmed or cancelled
    booked_at = Column(DateTime(timezone=True), server_default=func.now())