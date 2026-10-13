"""Categories used to classify campus issues."""

from enum import StrEnum


class IssueCategory(StrEnum):
    """Represent the type of campus problem reported."""

    ELECTRICAL = "electrical"
    FACILITIES = "facilities"
    CLEANLINESS = "cleanliness"
    NETWORK = "network"
    PLUMBING = "plumbing"
    SAFETY = "safety"
    OTHER = "other"