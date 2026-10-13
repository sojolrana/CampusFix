
"""Database model for the audit history of issue status changes."""

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.issue_status import IssueStatus


class IssueStatusHistory(Base):
    """Record a status transition and the user responsible for it."""

    __tablename__ = "issue_status_history"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    issue_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    old_status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status"),
        nullable=False,
    )
    new_status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status"),
        nullable=False,
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
