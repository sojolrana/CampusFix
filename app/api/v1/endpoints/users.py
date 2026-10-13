"""HTTP endpoints for user accounts."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import (
    EmailAlreadyRegisteredError,
    register_user,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Register a student account and return its public information."""
    try:
        user = await register_user(session, user_data)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from error

    return UserRead.model_validate(user)