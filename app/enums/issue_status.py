"""Allowed lifecycle statuses for campus issues."""

from enum import StrEnum


class IssueStatus(StrEnum):
    """Represent the progress of a reported campus issue."""

    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"