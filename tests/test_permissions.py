"""Tests for role-based authorization."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.permissions import require_roles
from app.enums.user_role import UserRole


def test_admin_role_is_allowed() -> None:
    """Allow an administrator through an admin-only permission check."""
    admin_user = SimpleNamespace(role=UserRole.ADMIN)
    check_admin_role = require_roles(UserRole.ADMIN)

    result = asyncio.run(check_admin_role(admin_user))

    assert result is admin_user


def test_student_role_is_forbidden_from_admin_action() -> None:
    """Reject a student who attempts an administrator-only action."""
    student_user = SimpleNamespace(role=UserRole.STUDENT)
    check_admin_role = require_roles(UserRole.ADMIN)

    with pytest.raises(HTTPException) as error:
        asyncio.run(check_admin_role(student_user))

    assert error.value.status_code == 403


def test_staff_and_admin_roles_are_allowed() -> None:
    """Allow both staff and administrators through a shared permission check."""
    staff_user = SimpleNamespace(role=UserRole.STAFF)
    check_staff_role = require_roles(UserRole.STAFF, UserRole.ADMIN)

    result = asyncio.run(check_staff_role(staff_user))

    assert result is staff_user