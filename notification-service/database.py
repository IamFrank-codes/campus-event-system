"""Database connection and session handling for the Notification Service."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings

DATABASE_URL = settings.database_url
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite://") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
