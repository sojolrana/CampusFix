"""HTTP endpoints for creating and listing campus issues."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.enums.user_role import UserRole
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueRead
from app.services.issue_service import get_user_issues, submit_issue


router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post(
    "",
    response_model=IssueRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_issue(
    issue_data: IssueCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.STUDENT)),
    ],
) -> IssueRead:
    """Create an issue report for the authenticated student."""
    issue = await submit_issue(
        session=session,
        reporter_id=current_user.id,
        issue_data=issue_data,
    )

    return IssueRead.model_validate(issue)


@router.get("", response_model=list[IssueRead])
async def list_issues(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[IssueRead]:
    """Return a paginated list of issues reported by the current user."""
    issues = await get_user_issues(
        session=session,
        reporter_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return [IssueRead.model_validate(issue) for issue in issues]