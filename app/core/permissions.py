"""Reusable authorization dependencies for user roles."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.enums.user_role import UserRole
from app.models.user import User


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    """Create a dependency that allows only the specified user roles."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """Reject authenticated users whose roles are not permitted."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker