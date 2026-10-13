"""Database operations for campus issues."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue


async def create_issue(session: AsyncSession, issue: Issue) -> Issue:
    """Save an issue and return it with database-generated values."""
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return issue


async def list_user_issues(
    session: AsyncSession,
    reporter_id: UUID,
    skip: int,
    limit: int,
) -> list[Issue]:
    """Return a paginated list of issues reported by one user."""
    statement = (
        select(Issue)
        .where(Issue.reporter_id == reporter_id)
        .order_by(Issue.created_at.desc(), Issue.id)
        .offset(skip)
        .limit(limit)
    )

    result = await session.scalars(statement)
    return list(result.all())