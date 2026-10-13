
"""HTTP endpoints for creating, listing, and managing campus issues."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.enums.user_role import UserRole
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueRead, IssueStatusUpdate
from app.services.issue_service import get_user_issues, submit_issue
from app.services.issue_workflow_service import (
    InvalidStatusTransitionError,
    IssueAccessError,
    IssueNotFoundError,
    get_visible_issue,
    update_issue_status,
)


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


@router.get("/{issue_id}", response_model=IssueRead)
async def get_issue_details(
    issue_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> IssueRead:
    """Return issue details to its reporter, assigned staff, or an admin."""

    try:
        issue = await get_visible_issue(
            session=session,
            issue_id=issue_id,
            current_user=current_user,
        )
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except IssueAccessError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return IssueRead.model_validate(issue)


@router.patch("/{issue_id}/status", response_model=IssueRead)
async def change_issue_status(
    issue_id: UUID,
    status_data: IssueStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.STAFF, UserRole.ADMIN)),
    ],
) -> IssueRead:
    """Change an issue status after checking permissions and transitions."""

    try:
        issue = await update_issue_status(
            session=session,
            issue_id=issue_id,
            new_status=status_data.status,
            current_user=current_user,
        )
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except IssueAccessError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return IssueRead.model_validate(issue)
