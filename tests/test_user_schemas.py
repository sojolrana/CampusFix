
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.enums.user_role import UserRole
from app.schemas.user import UserCreate, UserRead


def test_user_create_accepts_valid_data():
    """Accept valid registration data and normalize the full name."""

    user = UserCreate(
        full_name="  Sojol Rana  ",
        email="sojol@example.com",
        password="A-Strong-Password-123",
    )

    assert user.full_name == "Sojol Rana"
    assert str(user.email) == "sojol@example.com"
    assert user.password == "A-Strong-Password-123"


def test_user_create_rejects_short_password():
    """Reject a registration password shorter than 12 characters."""

    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Sojol Rana",
            email="sojol@example.com",
            password="short",
        )


def test_user_create_rejects_invalid_email():
    """Reject registration data containing an invalid email address."""

    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Sojol Rana",
            email="not-an-email",
            password="A-Strong-Password-123",
        )


def test_user_create_rejects_client_supplied_role():
    """Prevent clients from choosing their own account role."""

    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Sojol Rana",
            email="sojol@example.com",
            password="A-Strong-Password-123",
            role="admin",
        )


def test_user_read_does_not_expose_password_hash():
    """Ensure the public user schema excludes the stored password hash."""

    current_time = datetime.now(timezone.utc)

    orm_user = SimpleNamespace(
        id=uuid4(),
        full_name="Sojol Rana",
        email="sojol@example.com",
        hashed_password="a-placeholder-password-hash",
        role=UserRole.STUDENT,
        is_active=True,
        created_at=current_time,
        updated_at=current_time,
    )

    user = UserRead.model_validate(orm_user)
    response_data = user.model_dump()

    assert response_data["full_name"] == "Sojol Rana"
    assert response_data["role"] == UserRole.STUDENT
    assert "hashed_password" not in response_data
    assert "password" not in response_data
