
"""Integration tests for issue comments and status history."""

import asyncio
import os
from collections.abc import AsyncGenerator, Iterator
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.api.deps import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.enums.issue_category import IssueCategory
from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus
from app.enums.user_role import UserRole
from app.main import app
from app.models.issue import Issue
from app.models.issue_comment import IssueComment
from app.models.issue_status_history import IssueStatusHistory
from app.models.user import User


@pytest.fixture
def api_context() -> Iterator[dict[str, Any]]:
    """Provide a clean PostgreSQL test database and authenticated API client."""

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run issue activity integration tests.")

    parsed_url = make_url(database_url)

    if not parsed_url.database or "test" not in parsed_url.database.lower():
        pytest.fail(
            "TEST_DATABASE_URL must point to a dedicated database "
            "whose name contains 'test'."
        )

    if not parsed_url.drivername.startswith("postgresql+"):
        pytest.fail("These integration tests require PostgreSQL.")

    engine = create_async_engine(database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    identity: dict[str, User | None] = {"user": None}
    original_overrides = app.dependency_overrides.copy()

    async def reset_schema() -> None:
        """Recreate all application tables inside the test database."""

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    async def override_database() -> AsyncGenerator[AsyncSession, None]:
        """Provide a database session connected to the test database."""

        async with session_factory() as session:
            yield session

    async def override_identity() -> User:
        """Return the test user currently selected by the test case."""

        current_user = identity["user"]

        if current_user is None:
            raise RuntimeError("The test user has not been initialized.")

        return current_user

    async def seed_data() -> dict[str, Any]:
        """Create two students, two staff accounts, an admin, and an issue."""

        async with session_factory() as session:
            student_one = User(
                full_name="Student One",
                email="student-one@test.example",
                hashed_password="unused-test-hash",
                role=UserRole.STUDENT,
                is_active=True,
            )
            student_two = User(
                full_name="Student Two",
                email="student-two@test.example",
                hashed_password="unused-test-hash",
                role=UserRole.STUDENT,
                is_active=True,
            )
            assigned_staff = User(
                full_name="Assigned Staff",
                email="assigned-staff@test.example",
                hashed_password="unused-test-hash",
                role=UserRole.STAFF,
                is_active=True,
            )
            other_staff = User(
                full_name="Other Staff",
                email="other-staff@test.example",
                hashed_password="unused-test-hash",
                role=UserRole.STAFF,
                is_active=True,
            )
            admin = User(
                full_name="Test Admin",
                email="admin@test.example",
                hashed_password="unused-test-hash",
                role=UserRole.ADMIN,
                is_active=True,
            )

            session.add_all(
                [
                    student_one,
                    student_two,
                    assigned_staff,
                    other_staff,
                    admin,
                ]
            )
            await session.flush()

            issue = Issue(
                title="Broken classroom light",
                description="The classroom light is not working.",
                category=IssueCategory.ELECTRICAL,
                location="Classroom A101",
                status=IssueStatus.SUBMITTED,
                priority=IssuePriority.NORMAL,
                reporter_id=student_one.id,
                assigned_staff_id=assigned_staff.id,
            )

            resolved_issue = Issue(
                title="Resolved network problem",
                description="The classroom network problem was resolved.",
                category=IssueCategory.NETWORK,
                location="Computer Lab",
                status=IssueStatus.RESOLVED,
                priority=IssuePriority.NORMAL,
                reporter_id=student_one.id,
                assigned_staff_id=assigned_staff.id,
            )

            session.add_all([issue, resolved_issue])
            await session.commit()
            await session.refresh(issue)
            await session.refresh(resolved_issue)

            return {
                "student_one": student_one,
                "student_two": student_two,
                "assigned_staff": assigned_staff,
                "other_staff": other_staff,
                "admin": admin,
                "issue_id": issue.id,
                "resolved_issue_id": resolved_issue.id,
            }

    try:
        asyncio.run(reset_schema())

        app.dependency_overrides[get_db] = override_database
        app.dependency_overrides[get_current_user] = override_identity

        with TestClient(app) as client:
            data = asyncio.run(seed_data())
            identity["user"] = data["student_one"]

            yield {
                "client": client,
                "identity": identity,
                **data,
            }
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

        async def dispose_engine() -> None:
            """Remove test tables and close test database connections."""

            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)

            await engine.dispose()

        asyncio.run(dispose_engine())


def test_student_can_comment_on_own_issue(api_context: dict[str, Any]) -> None:
    """Verify that a student can create and retrieve their own issue comment."""

    client = api_context["client"]
    identity = api_context["identity"]
    student = api_context["student_one"]
    issue_id = api_context["issue_id"]

    identity["user"] = student

    response = client.post(
        f"/api/v1/issues/{issue_id}/comments",
        json={"body": "The light is still flickering."},
    )

    assert response.status_code == 201
    assert response.json()["body"] == "The light is still flickering."
    assert response.json()["author_id"] == str(student.id)

    comments_response = client.get(
        f"/api/v1/issues/{issue_id}/comments"
    )

    assert comments_response.status_code == 200
    assert len(comments_response.json()) == 1


def test_student_cannot_comment_on_another_students_issue(
    api_context: dict[str, Any],
) -> None:
    """Verify that students cannot comment on issues owned by other students."""

    client = api_context["client"]
    identity = api_context["identity"]

    identity["user"] = api_context["student_two"]

    response = client.post(
        f"/api/v1/issues/{api_context['issue_id']}/comments",
        json={"body": "I should not be able to comment here."},
    )

    assert response.status_code == 403


def test_assigned_staff_status_change_creates_history(
    api_context: dict[str, Any],
) -> None:
    """Verify that a valid status change produces an audit history entry."""

    client = api_context["client"]
    identity = api_context["identity"]
    staff = api_context["assigned_staff"]
    issue_id = api_context["issue_id"]

    identity["user"] = staff

    response = client.patch(
        f"/api/v1/issues/{issue_id}/status",
        json={"status": "acknowledged"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"

    history_response = client.get(
        f"/api/v1/issues/{issue_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["old_status"] == "submitted"
    assert history[0]["new_status"] == "acknowledged"
    assert history[0]["changed_by_id"] == str(staff.id)


def test_unassigned_staff_cannot_read_issue_history(
    api_context: dict[str, Any],
) -> None:
    """Verify that staff members cannot read history of unassigned issues."""

    client = api_context["client"]
    identity = api_context["identity"]

    identity["user"] = api_context["other_staff"]

    response = client.get(
        f"/api/v1/issues/{api_context['issue_id']}/history"
    )

    assert response.status_code == 403


def test_invalid_status_transition_creates_no_history(
    api_context: dict[str, Any],
) -> None:
    """Verify that an invalid transition is rejected without an audit entry."""

    client = api_context["client"]
    identity = api_context["identity"]
    staff = api_context["assigned_staff"]
    issue_id = api_context["resolved_issue_id"]

    identity["user"] = staff

    response = client.patch(
        f"/api/v1/issues/{issue_id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 422

    history_response = client.get(
        f"/api/v1/issues/{issue_id}/history"
    )

    assert history_response.status_code == 200
    assert history_response.json() == []


def test_unknown_issue_history_returns_404(
    api_context: dict[str, Any],
) -> None:
    """Verify that requesting history for a missing issue returns 404."""

    client = api_context["client"]
    identity = api_context["identity"]

    identity["user"] = api_context["student_one"]

    unknown_issue_id = uuid4()

    response = client.get(
        f"/api/v1/issues/{unknown_issue_id}/history"
    )

    assert response.status_code == 404


def test_comment_validation_rejects_empty_body(
    api_context: dict[str, Any],
) -> None:
    """Verify that whitespace-only comments are rejected by request validation."""

    client = api_context["client"]
    identity = api_context["identity"]

    identity["user"] = api_context["student_one"]

    response = client.post(
        f"/api/v1/issues/{api_context['issue_id']}/comments",
        json={"body": "   "},
    )

    assert response.status_code == 422
