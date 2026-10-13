"""Pydantic schemas for creating and reading campus issues."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from app.enums.issue_category import IssueCategory
from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus
from app.schemas.base import ORMReadSchema, SchemaBase


IssueTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=5, max_length=150),
]

IssueDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=10, max_length=5000),
]

IssueLocation = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=200),
]


class IssueCreate(SchemaBase):
    """Validate the information required to submit a campus issue."""

    title: IssueTitle
    description: IssueDescription
    category: IssueCategory
    location: IssueLocation


class IssueRead(ORMReadSchema):
    """Define the issue information returned by the API."""

    id: UUID
    title: str
    description: str
    category: IssueCategory
    location: str
    status: IssueStatus
    priority: IssuePriority
    reporter_id: UUID
    created_at: datetime
    updated_at: datetime