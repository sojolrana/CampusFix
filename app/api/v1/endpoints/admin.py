"""Administrative HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.db.session import get_db
from app.enums.user_role import UserRole
from app.models.user import User
from app.schemas.user import UserRead
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