
"""Pydantic schemas for issue comments and status history."""

from datetime import datetime
from uuid import UUID

from app.enums.issue_status import IssueStatus
from app.schemas.base import ORMReadSchema


class IssueCommentRead(ORMReadSchema):
    """Define a comment returned by the API."""

    id: UUID
    issue_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime


class IssueStatusHistoryRead(ORMReadSchema):
    """Define a status-history entry returned by the API."""

    id: UUID
    issue_id: UUID
    changed_by_id: UUID
    old_status: IssueStatus
    new_status: IssueStatus
    changed_at: datetime
