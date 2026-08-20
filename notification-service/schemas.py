"""Pydantic request and response schemas for the Notification API."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class NotificationType(str, Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    EVENT_REMINDER = "event_reminder"
    EVENT_UPDATE = "event_update"
    GENERAL = "general"

class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    event_id: int | None = Field(None, gt=0)
    notification_type: NotificationType = NotificationType.BOOKING_CONFIRMATION
    message: str = Field(..., min_length=1, max_length=1000)

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int | None
    notification_type: NotificationType
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
