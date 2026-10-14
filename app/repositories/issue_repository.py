
"""Database operations for campus issues."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.issue_category import IssueCategory
from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus
from app.enums.user_role import UserRole
from app.models.issue import Issue
from app.models.user import User


async def create_issue(
    session: AsyncSession,
    issue: Issue,
) -> Issue:
    """Save an issue and return it with database-generated values."""
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return issue


async def list_user_issues(
    session: AsyncSession,
    reporter_id: UUID,
    skip: int = 0,
    limit: int = 20,
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


async def list_issues(
    session: AsyncSession,
    current_user: User,
    skip: int = 0,
    limit: int = 20,
    issue_status: IssueStatus | None = None,
    category: IssueCategory | None = None,
    priority: IssuePriority | None = None,
    assigned_staff_id: UUID | None = None,
    sort_order: str = "newest",
) -> list[Issue]:
    """Return a filtered issue page scoped to the current user's role."""
    statement = select(Issue)

    # Apply the access scope before the optional filters.
    if current_user.role == UserRole.STUDENT:
        statement = statement.where(
            Issue.reporter_id == current_user.id
        )
    elif current_user.role == UserRole.STAFF:
        statement = statement.where(
            Issue.assigned_staff_id == current_user.id
        )
    elif current_user.role != UserRole.ADMIN:
        return []

    if issue_status is not None:
        statement = statement.where(Issue.status == issue_status)

    if category is not None:
        statement = statement.where(Issue.category == category)

    if priority is not None:
        statement = statement.where(Issue.priority == priority)

    if assigned_staff_id is not None:
        statement = statement.where(
            Issue.assigned_staff_id == assigned_staff_id
        )

    if sort_order == "oldest":
        statement = statement.order_by(
            Issue.created_at.asc(),
            Issue.id.asc(),
        )
    else:
        statement = statement.order_by(
            Issue.created_at.desc(),
            Issue.id.asc(),
        )

    statement = statement.offset(skip).limit(limit)

    result = await session.scalars(statement)
    return list(result.all())
