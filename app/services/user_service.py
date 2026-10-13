"""Application logic for user registration."""

from starlette.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.enums.user_role import UserRole
from app.models.user import User
from app.repositories import user_repository
from app.repositories.user_repository import DuplicateEmailError
from app.schemas.user import UserCreate


class EmailAlreadyRegisteredError(Exception):
    """Represent an email address that already belongs to an account."""


async def register_user(
    session: AsyncSession,
    user_data: UserCreate,
) -> User:
    """Validate registration uniqueness, hash the password, and create a student account."""
    email = str(user_data.email)

    existing_user = await user_repository.get_by_email(session, email)

    if existing_user is not None:
        raise EmailAlreadyRegisteredError

    hashed_password = await run_in_threadpool(
        hash_password,
        user_data.password,
    )

    user = User(
        full_name=user_data.full_name,
        email=email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT,
    )

    try:
        return await user_repository.create(session, user)
    except DuplicateEmailError as error:
        raise EmailAlreadyRegisteredError from error


async def list_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[User]:
    """Retrieve a paginated collection of users for administrative operations."""
    return await user_repository.list_users(
        session=session,
        skip=skip,
        limit=limit,
    )