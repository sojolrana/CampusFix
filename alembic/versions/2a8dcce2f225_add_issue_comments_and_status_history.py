
"""Add issue comments and status history.

Revision ID: 2a8dcce2f225
Revises: 2ee3f8a6e9f3
Create Date: 2026-10-13 22:30:27.234965
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers used by Alembic.
revision: str = "2a8dcce2f225"
down_revision: Union[str, Sequence[str], None] = "2ee3f8a6e9f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create issue comment and status history tables."""

    op.create_table(
        "issue_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("issue_id", sa.UUID(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["issue_id"],
            ["issues.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_issue_comments_author_id"),
        "issue_comments",
        ["author_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_issue_comments_issue_id"),
        "issue_comments",
        ["issue_id"],
        unique=False,
    )

    # Reuse the issue_status enum already created by the issues migration.
    existing_issue_status_enum = postgresql.ENUM(
        "SUBMITTED",
        "ACKNOWLEDGED",
        "IN_PROGRESS",
        "RESOLVED",
        "REJECTED",
        name="issue_status",
        create_type=False,
    )

    op.create_table(
        "issue_status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("issue_id", sa.UUID(), nullable=False),
        sa.Column("changed_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "old_status",
            existing_issue_status_enum,
            nullable=False,
        ),
        sa.Column(
            "new_status",
            existing_issue_status_enum,
            nullable=False,
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["issue_id"],
            ["issues.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_issue_status_history_changed_by_id"),
        "issue_status_history",
        ["changed_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_issue_status_history_issue_id"),
        "issue_status_history",
        ["issue_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove issue history and comment tables."""

    op.drop_index(
        op.f("ix_issue_status_history_issue_id"),
        table_name="issue_status_history",
    )
    op.drop_index(
        op.f("ix_issue_status_history_changed_by_id"),
        table_name="issue_status_history",
    )
    op.drop_table("issue_status_history")

    op.drop_index(
        op.f("ix_issue_comments_issue_id"),
        table_name="issue_comments",
    )
    op.drop_index(
        op.f("ix_issue_comments_author_id"),
        table_name="issue_comments",
    )
    op.drop_table("issue_comments")
