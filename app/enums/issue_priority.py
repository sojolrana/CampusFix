"""Allowed priority levels for campus issues."""

from enum import StrEnum


class IssuePriority(StrEnum):
    """Represent the urgency assigned to a campus issue."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"