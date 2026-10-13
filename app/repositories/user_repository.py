"""Database operations for user records."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from app.models.user import User


class DuplicateEmailError(Exception):
    """Represent an attempt to create a user with an email already in use."""


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Return the user with the given email, or None if no user exists."""
    statement = select(User).where(User.email == email)
    return await session.scalar(statement)


async def create(session: AsyncSession, user: User) -> User:
    """Save a user and return the database-refreshed ORM object.

    Raise DuplicateEmailError when the database reports a duplicate email.
    Re-raise other integrity errors instead of misreporting them.
    """
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()

        original_error = error.orig
        diagnostics = getattr(original_error, "diag", None)
        constraint_name = getattr(diagnostics, "constraint_name", None)
        sqlstate = getattr(original_error, "sqlstate", None)

        if sqlstate == "23505" and constraint_name == "ix_users_email":
            raise DuplicateEmailError from error

        raise

    await session.refresh(user)
    return user

async def get_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    """Return the user with the given UUID, or None if no user exists."""
    return await session.get(User, user_id)

async def list_users(
    session: AsyncSession,
    skip: int,
    limit: int,
) -> list[User]:
    """Return a page of users ordered from newest to oldest."""
    statement = (
        select(User)
        .order_by(User.created_at.desc(), User.id)
        .offset(skip)
        .limit(limit)
    )

    result = await session.scalars(statement)
    return list(result.all())