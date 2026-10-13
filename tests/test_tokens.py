"""Tests for JWT access-token creation and expiration."""

from datetime import timedelta
from uuid import UUID

import jwt
import pytest

from app.core.config import settings
from app.core.tokens import create_access_token


def test_access_token_contains_user_id() -> None:
    """Verify a valid token contains the expected user ID."""
    user_id = "8a7e2c50-21d4-4f3c-97d2-bb80d0bb7b8e"
    token = create_access_token(user_id=UUID(user_id))

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == user_id
    assert "exp" in payload
    assert "iat" in payload


def test_expired_access_token_is_rejected() -> None:
    """Ensure a token that has expired cannot be decoded successfully."""
    from uuid import UUID

    token = create_access_token(
        user_id=UUID("8a7e2c50-21d4-4f3c-97d2-bb80d0bb7b8e"),
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )