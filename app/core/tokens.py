"""Utilities for creating and validating JWT access tokens."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.core.config import settings


def create_access_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT containing the user's ID and an expiration time."""
    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )