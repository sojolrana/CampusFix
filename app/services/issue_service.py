"""Business logic for campus issue management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus
from app.models.issue import Issue
from app.repositories.issue_repository import (
    create_issue,
    list_user_issues,
)
from app.schemas.issue import IssueCreate


async def submit_issue(
    session: AsyncSession,
    reporter_id: UUID,
    issue_data: IssueCreate,
) -> Issue:
    """Create a new issue for the authenticated reporter."""
    issue = Issue(
        title=issue_data.title,
        description=issue_data.description,
        category=issue_data.category,
        location=issue_data.location,
        reporter_id=reporter_id,
        status=IssueStatus.SUBMITTED,
        priority=IssuePriority.NORMAL,
    )

    return await create_issue(session, issue)


async def get_user_issues(
    session: AsyncSession,
    reporter_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> list[Issue]:
    """Retrieve a page of issues belonging to the authenticated reporter."""
    return await list_user_issues(
        session=session,
        reporter_id=reporter_id,
        skip=skip,
        limit=limit,
    )