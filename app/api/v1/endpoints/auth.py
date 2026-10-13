"""HTTP endpoints for login and authenticated-user information."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.tokens import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Verify login credentials and issue an access token."""
    user = await authenticate_user(
        session,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or inactive account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Return the public profile of the authenticated user."""
    return UserRead.model_validate(current_user)