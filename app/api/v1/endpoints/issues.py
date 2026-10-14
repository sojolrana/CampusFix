
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
from app.schemas.issue import (
    IssueAssign,
    IssueCommentCreate,
    IssueCreate,
    IssueRead,
    IssueStatusUpdate,
)
from app.enums.issue_category import IssueCategory
from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus

from app.services.issue_service import get_issues, submit_issue
from app.services.issue_workflow_service import (
    InvalidStatusTransitionError,
    IssueAccessError,
    IssueNotFoundError,
    get_visible_issue,
    update_issue_status,
)
from app.schemas.issue_activity import (
    IssueCommentRead,
    IssueStatusHistoryRead,
)
from app.services.issue_activity_service import (
    create_issue_comment,
    list_issue_comments,
    list_issue_status_history,
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
    issue_status: IssueStatus | None = Query(
        default=None,
        alias="status",
    ),
    category: IssueCategory | None = None,
    priority: IssuePriority | None = None,
    assigned_staff_id: UUID | None = None,
    sort_order: Annotated[
        str,
        Query(pattern="^(newest|oldest)$"),
    ] = "newest",
) -> list[IssueRead]:
    """List visible issues with filtering, sorting, and pagination."""
    if (
        assigned_staff_id is not None
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can filter by assigned staff.",
        )

    issues = await get_issues(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit,
        issue_status=issue_status,
        category=category,
        priority=priority,
        assigned_staff_id=assigned_staff_id,
        sort_order=sort_order,
    )

    return [
        IssueRead.model_validate(issue)
        for issue in issues
    ]


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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return IssueRead.model_validate(issue)


@router.post(
    "/{issue_id}/comments",
    response_model=IssueCommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_issue_comment(
    issue_id: UUID,
    comment_data: IssueCommentCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> IssueCommentRead:
    """Add a comment to an issue the current user can access."""

    try:
        comment = await create_issue_comment(
            session=session,
            issue_id=issue_id,
            author=current_user,
            body=comment_data.body,
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

    return IssueCommentRead.model_validate(comment)


@router.get(
    "/{issue_id}/comments",
    response_model=list[IssueCommentRead],
)
async def get_issue_comments(
    issue_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[IssueCommentRead]:
    """List comments for an issue the current user can access."""

    try:
        comments = await list_issue_comments(
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

    return [
        IssueCommentRead.model_validate(comment)
        for comment in comments
    ]


@router.get(
    "/{issue_id}/history",
    response_model=list[IssueStatusHistoryRead],
)
async def get_issue_history(
    issue_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[IssueStatusHistoryRead]:
    """List status changes for an issue the current user can access."""

    try:
        history = await list_issue_status_history(
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

    return [
        IssueStatusHistoryRead.model_validate(entry)
        for entry in history
    ]
