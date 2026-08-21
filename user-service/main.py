"""
main.py
User / Auth Service - Campus Event Management System

Handles registration, login, and profile management for students,
event organizers, and admins. This is one independent microservice;
it owns its own database (users.db) and can be started/stopped/tested
completely separately from the other services in the system.

Run with:
    uvicorn main:app --reload --port 8001
Then visit http://127.0.0.1:8001/docs for interactive API docs.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError

from database import Base, engine, get_db
import models
import schemas
from settings import settings
import auth
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Creates the users table on startup if it doesn't already exist
Base.metadata.create_all(bind=engine)



app = FastAPI(
    title="User / Auth Service",
    description="Handles registration, login and profiles for the Campus Event Management System",
    version="1.0.0",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(","))

# Clients authenticate through the JSON login endpoint and send the returned JWT
# as: Authorization: Bearer <token>. The Swagger-only form token helper is removed.
authorization_header = APIKeyHeader(name="Authorization", auto_error=True)


def get_current_user(authorization: str = Depends(authorization_header), db: Session = Depends(get_db)) -> models.User:
    """
    Dependency that protects routes requiring login.
    Decodes the JWT from the request, looks up the user, and raises
    a 401 error if anything about the token or user is invalid.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise credentials_error
        payload = auth.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except (JWTError, ValueError):
        raise credentials_error

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_error
    return user


@app.get("/health")
def health_check():
    """Simple endpoint other services (or a load balancer) can ping to check this service is alive."""
    return {"status": "ok", "service": "user-auth-service"}


@app.post("/api/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new student, organizer, or admin account."""
    new_user = models.User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        # Most likely cause: the email is already registered (unique constraint)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    db.refresh(new_user)
    return new_user


@app.post("/api/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Verifies email/password and returns a JWT access token if correct."""
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = auth.create_access_token(data={"sub": str(user.id), "role": user.role})
    return schemas.Token(access_token=token)



@app.get("/api/users/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Returns the profile of whoever's token was sent - a protected route."""
    return current_user


@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Looks up any user by id - useful for other services (e.g. Booking) to verify a user exists."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.put("/api/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Updates a user's own profile. Users can only update themselves."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if updates.full_name is not None:
        user.full_name = updates.full_name

    db.commit()
    db.refresh(user)
    return user