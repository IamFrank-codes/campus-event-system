"""
auth.py
Handles password hashing and JWT token creation/verification.
Other services (Booking, Event, etc.) will use the SAME SECRET_KEY
to verify tokens issued by this service - that's how auth is shared
across a microservices system without a central session store.
"""

import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

# In a real deployment, load this from an environment variable, never hardcode it.
# For this student project, a .env file or os.environ is enough.
from settings import settings
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Turns a plain text password into a secure hash before storing it."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a login attempt's password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Creates a signed JWT token containing the given data (e.g. user id, role)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Raises JWTError if the token is invalid or expired - the calling
    route is responsible for turning that into a proper HTTP error.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])