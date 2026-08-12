"""
models.py
Defines the User table structure using SQLAlchemy's ORM.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # role is one of: "student", "organizer", "admin"
    role = Column(String, nullable=False, default="student")
    created_at = Column(DateTime(timezone=True), server_default=func.now())