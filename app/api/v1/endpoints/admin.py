
"""Administrative HTTP endpoints for users and issue assignment."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.db.session import get_db
from app.enums.user_role import UserRole
from app.models.user import User
from app.schemas.issue import IssueAssign, IssueRead
from app.schemas.user import UserRead
from app.services.issue_workflow_service import (
    IssueNotFoundError,
    StaffNotFoundError,
    assign_issue_to_staff,
)
from app.services.user_service import list_users


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get("/users", response_model=list[UserRead])
async def get_users(
    session: Annotated[AsyncSession, Depends(get_db)],
    _admin_user: Annotated[
        User,
        Depends(require_roles(UserRole.ADMIN)),
    ],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[UserRead]:
    """Return a paginated user list to authenticated administrators."""

    users = await list_users(
        session=session,
        skip=skip,
        limit=limit,
    )

    return [UserRead.model_validate(user) for user in users]


@router.patch(
    "/issues/{issue_id}/assign",
    response_model=IssueRead,
)
async def assign_issue(
    issue_id: UUID,
    assignment: IssueAssign,
    session: Annotated[AsyncSession, Depends(get_db)],
    _admin_user: Annotated[
        User,
        Depends(require_roles(UserRole.ADMIN)),
    ],
) -> IssueRead:
    """Assign an existing issue to an active staff member."""

    try:
        issue = await assign_issue_to_staff(
            session=session,
            issue_id=issue_id,
            staff_id=assignment.staff_id,
        )
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return IssueRead.model_validate(issue)
