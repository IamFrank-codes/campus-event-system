"""Persistence models for notifications."""
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_id = Column(Integer, nullable=True, index=True)
    notification_type = Column(String(40), nullable=False, default="booking_confirmation")
    message = Column(String(1000), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
