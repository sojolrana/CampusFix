"""Tests for campus issue request validation."""

import pytest
from pydantic import ValidationError

from app.enums.issue_category import IssueCategory
from app.schemas.issue import IssueCreate


def test_valid_issue_data_is_accepted() -> None:
    """Accept a correctly formed campus issue report."""
    issue = IssueCreate(
        title="Broken classroom fan",
        description="The ceiling fan in room 204 is not working.",
        category=IssueCategory.FACILITIES,
        location="Academic Building, Room 204",
    )

    assert issue.title == "Broken classroom fan"
    assert issue.category == IssueCategory.FACILITIES


def test_short_title_is_rejected() -> None:
    """Reject an issue title that is shorter than five characters."""
    with pytest.raises(ValidationError):
        IssueCreate(
            title="Fan",
            description="The ceiling fan is not working properly.",
            category=IssueCategory.FACILITIES,
            location="Room 204",
        )


def test_invalid_category_is_rejected() -> None:
    """Reject a category that is not one of the supported values."""
    with pytest.raises(ValidationError):
        IssueCreate(
            title="Broken classroom fan",
            description="The ceiling fan is not working properly.",
            category="something_invalid",
            location="Room 204",
        )


def test_client_cannot_set_reporter_or_status() -> None:
    """Reject fields that clients are not allowed to supply."""
    with pytest.raises(ValidationError):
        IssueCreate(
            title="Broken classroom fan",
            description="The ceiling fan in room 204 is not working.",
            category=IssueCategory.FACILITIES,
            location="Room 204",
            reporter_id="8a7e2c50-21d4-4f3c-97d2-bb80d0bb7b8e",
            status="resolved",
        )