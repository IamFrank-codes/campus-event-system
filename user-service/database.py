"""
database.py
Sets up the SQLite database connection and session handling for the User/Auth service.
Each microservice in this system owns its own database - this one only ever
stores user/auth data, nothing else.
"""

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base 

# SQLite file will be created automatically in this folder on first run
from settings import settings
DATABASE_URL = settings.database_url

# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI can handle requests across multiple threads
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency used by FastAPI routes to get a database session.
    Ensures the session is always closed after the request finishes,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()