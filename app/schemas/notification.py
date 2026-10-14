
"""Pydantic schemas for reading and updating notifications."""

from datetime import datetime
from uuid import UUID

from app.schemas.base import ORMReadSchema, SchemaBase


class NotificationRead(ORMReadSchema):
    """Define the notification information returned by the API."""

    id: UUID
    recipient_id: UUID
    issue_id: UUID | None
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None


class NotificationReadUpdate(SchemaBase):
    """Validate a request to mark a notification as read."""

    is_read: bool
