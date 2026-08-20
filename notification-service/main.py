"""Notification Service for the Campus Event Management System."""
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
import httpx

from database import Base, engine, get_db
import models
import schemas
from security import current_claims, require_roles
from settings import settings
from starlette.middleware.trustedhost import TrustedHostMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Notification Service",
    description="Creates and retrieves simulated campus event notifications",
    version="2.0.0",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(","))

USER_SERVICE_URL = settings.user_service_url
EVENT_SERVICE_URL = settings.event_service_url


def verify_user(user_id: int) -> None:
    try:
        response = httpx.get(f"{USER_SERVICE_URL}/api/users/{user_id}", timeout=5.0)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="User service is unavailable") from exc
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="User service is unavailable")
    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail="User could not be verified")


def verify_event(event_id: int) -> None:
    try:
        response = httpx.get(f"{EVENT_SERVICE_URL}/api/events/{event_id}", timeout=5.0)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Event service is unavailable") from exc
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Event not found")
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="Event service is unavailable")
    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail="Event could not be verified")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification-service"}


@app.post("/api/notifications/send", response_model=schemas.NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_notification(
    notification_in: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_roles("student", "organizer", "admin")),
):
    if claims.get("role") != "admin" and int(claims["sub"]) != notification_in.user_id:
        raise HTTPException(status_code=403, detail="User id must match the authenticated user")
    verify_user(notification_in.user_id)
    if notification_in.event_id is not None:
        verify_event(notification_in.event_id)
    notification = models.Notification(**notification_in.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@app.get("/api/notifications/user/{user_id}", response_model=list[schemas.NotificationResponse])
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(current_claims),
):
    if claims.get("role") != "admin" and int(claims["sub"]) != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own notifications")
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc()).all()


@app.patch("/api/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(current_claims),
):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if claims.get("role") != "admin" and int(claims["sub"]) != notification.user_id:
        raise HTTPException(status_code=403, detail="You can only update your own notifications")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
