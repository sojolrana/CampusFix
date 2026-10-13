"""Application logic for authenticating users."""

from starlette.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository


DUMMY_PASSWORD_HASH = hash_password("not-a-real-user-password")


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Return an active user if the email and password are valid."""
    user = await user_repository.get_by_email(session, email)

    if user is None:
        await run_in_threadpool(verify_password, password, DUMMY_PASSWORD_HASH)
        return None

    password_is_valid = await run_in_threadpool(
        verify_password,
        password,
        user.hashed_password,
    )

    if not password_is_valid or not user.is_active:
        return None

    return user