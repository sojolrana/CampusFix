
"""Pydantic schemas for issue comments."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from app.schemas.base import ORMReadSchema, SchemaBase


CommentBody = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=3000),
]


class IssueCommentCreate(SchemaBase):
    """Validate the text submitted for a new issue comment."""

    body: CommentBody


class IssueCommentRead(ORMReadSchema):
    """Define the comment information returned by the API."""

    id: UUID
    issue_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime
