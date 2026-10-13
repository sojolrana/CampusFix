"""SQLAlchemy model for campus issue reports."""

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.issue_category import IssueCategory
from app.enums.issue_priority import IssuePriority
from app.enums.issue_status import IssueStatus


class Issue(Base):
    """Represent an issue reported by a campus user."""

    __tablename__ = "issues"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[IssueCategory] = mapped_column(
        Enum(IssueCategory, name="issue_category"),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(String(200), nullable=False)

    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status"),
        nullable=False,
        default=IssueStatus.SUBMITTED,
    )
    priority: Mapped[IssuePriority] = mapped_column(
        Enum(IssuePriority, name="issue_priority"),
        nullable=False,
        default=IssuePriority.NORMAL,
    )

    reporter_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    assigned_staff_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
