
"""Business logic for creating and managing user notifications."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    session: AsyncSession,
    recipient_id: UUID,
    title: str,
    message: str,
    issue_id: UUID | None = None,
) -> Notification:
    """Add a notification to the current transaction without committing it."""

    notification = Notification(
        recipient_id=recipient_id,
        issue_id=issue_id,
        title=title,
        message=message,
    )

    session.add(notification)
    await session.flush()

    return notification


async def list_notifications(
    session: AsyncSession,
    recipient_id: UUID,
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
) -> list[Notification]:
    """Return a page of notifications belonging to one recipient."""

    statement = select(Notification).where(
        Notification.recipient_id == recipient_id
    )

    if unread_only:
        statement = statement.where(Notification.is_read.is_(False))

    statement = (
        statement
        .order_by(Notification.created_at.desc(), Notification.id)
        .offset(skip)
        .limit(limit)
    )

    result = await session.scalars(statement)
    return list(result.all())


async def count_unread_notifications(
    session: AsyncSession,
    recipient_id: UUID,
) -> int:
    """Count unread notifications belonging to one recipient."""

    statement = select(func.count()).select_from(Notification).where(
        Notification.recipient_id == recipient_id,
        Notification.is_read.is_(False),
    )

    return int(await session.scalar(statement) or 0)


async def mark_notification_read(
    session: AsyncSession,
    notification_id: UUID,
    recipient_id: UUID,
) -> Notification | None:
    """Mark a notification as read only if it belongs to the recipient."""

    result = await session.scalars(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id,
        )
    )

    notification = result.one_or_none()

    if notification is None:
        return None

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(notification)

    return notification
