
"""Business logic for issue comments and status history."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue
from app.models.issue_comment import IssueComment
from app.models.issue_status_history import IssueStatusHistory
from app.models.user import User
from app.schemas.issue import IssueCreate
from app.services.issue_workflow_service import (
    get_visible_issue,
)


async def create_issue_comment(
    session: AsyncSession,
    issue_id: UUID,
    author: User,
    body: str,
) -> IssueComment:
    """Create a comment after verifying access to the issue."""

    await get_visible_issue(
        session=session,
        issue_id=issue_id,
        current_user=author,
    )

    comment = IssueComment(
        issue_id=issue_id,
        author_id=author.id,
        body=body,
    )

    session.add(comment)

    try:
        await session.commit()
        await session.refresh(comment)
    except Exception:
        await session.rollback()
        raise

    return comment


async def list_issue_comments(
    session: AsyncSession,
    issue_id: UUID,
    current_user: User,
) -> list[IssueComment]:
    """Return comments in chronological order after checking issue access."""

    await get_visible_issue(
        session=session,
        issue_id=issue_id,
        current_user=current_user,
    )

    result = await session.scalars(
        select(IssueComment)
        .where(IssueComment.issue_id == issue_id)
        .order_by(IssueComment.created_at, IssueComment.id)
    )

    return list(result.all())


async def list_issue_status_history(
    session: AsyncSession,
    issue_id: UUID,
    current_user: User,
) -> list[IssueStatusHistory]:
    """Return an issue's status history after checking access."""

    await get_visible_issue(
        session=session,
        issue_id=issue_id,
        current_user=current_user,
    )

    result = await session.scalars(
        select(IssueStatusHistory)
        .where(IssueStatusHistory.issue_id == issue_id)
        .order_by(
            IssueStatusHistory.changed_at,
            IssueStatusHistory.id,
        )
    )

    return list(result.all())
