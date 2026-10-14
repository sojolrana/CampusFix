
"""HTTP endpoints for viewing and updating personal notifications."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.services.notification_service import (
    count_unread_notifications,
    list_notifications,
    mark_notification_read,
)


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationRead])
async def get_notifications(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    unread_only: bool = False,
) -> list[NotificationRead]:
    """Return a page of notifications for the authenticated user."""

    notifications = await list_notifications(
        session=session,
        recipient_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )

    return [
        NotificationRead.model_validate(notification)
        for notification in notifications
    ]


@router.get("/unread-count")
async def get_unread_count(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, int]:
    """Return the number of unread notifications for the current user."""

    count = await count_unread_notifications(
        session=session,
        recipient_id=current_user.id,
    )

    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_as_read(
    notification_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NotificationRead:
    """Mark one of the current user's notifications as read."""

    notification = await mark_notification_read(
        session=session,
        notification_id=notification_id,
        recipient_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return NotificationRead.model_validate(notification)
