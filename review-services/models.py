"""
models.py
Defines the Review table structure.
"""

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, UniqueConstraint
from sqlalchemy.sql import func
from database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_review_event_student"),)
    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_review_event_student"),)

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
