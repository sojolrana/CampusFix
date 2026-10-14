
"""Business rules for issue visibility, assignment, and status changes."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.issue_status import IssueStatus
from app.enums.user_role import UserRole
from app.models.issue import Issue
from app.models.user import User
from app.models.issue_status_history import IssueStatusHistory
from app.services.notification_service import create_notification


class IssueNotFoundError(Exception):
    """Indicate that the requested issue does not exist."""


class StaffNotFoundError(Exception):
    """Indicate that no eligible staff account was found."""


class IssueAccessError(Exception):
    """Indicate that the current user cannot access or modify an issue."""


class InvalidStatusTransitionError(Exception):
    """Indicate that a requested status transition is not allowed."""


_ALLOWED_TRANSITIONS = {
    IssueStatus.SUBMITTED: {
        IssueStatus.ACKNOWLEDGED,
        IssueStatus.REJECTED,
    },
    IssueStatus.ACKNOWLEDGED: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.REJECTED,
    },
    IssueStatus.IN_PROGRESS: {
        IssueStatus.RESOLVED,
    },
    IssueStatus.RESOLVED: set(),
    IssueStatus.REJECTED: set(),
}


async def get_issue_by_id(
    session: AsyncSession,
    issue_id: UUID,
) -> Issue:
    """Retrieve an issue by UUID or raise an issue-not-found error."""

    result = await session.scalars(
        select(Issue).where(Issue.id == issue_id)
    )
    issue = result.one_or_none()

    if issue is None:
        raise IssueNotFoundError("Issue not found.")

    return issue


async def get_visible_issue(
    session: AsyncSession,
    issue_id: UUID,
    current_user: User,
) -> Issue:
    """Return an issue only if the user is its reporter, assigned staff, or admin."""

    issue = await get_issue_by_id(session, issue_id)

    if current_user.role == UserRole.ADMIN:
        return issue

    if current_user.role == UserRole.STAFF:
        if issue.assigned_staff_id == current_user.id:
            return issue

        raise IssueAccessError("This issue is not assigned to you.")

    if issue.reporter_id == current_user.id:
        return issue

    raise IssueAccessError("You cannot access this issue.")


async def assign_issue_to_staff(
    session: AsyncSession,
    issue_id: UUID,
    staff_id: UUID,
) -> Issue:
    """Assign an issue to active staff and notify the assigned person."""

    issue = await get_issue_by_id(session, issue_id)

    result = await session.scalars(
        select(User).where(
            User.id == staff_id,
            User.role == UserRole.STAFF,
            User.is_active.is_(True),
        )
    )
    staff_member = result.one_or_none()

    if staff_member is None:
        raise StaffNotFoundError(
            "The selected active staff account was not found."
        )

    previous_staff_id = issue.assigned_staff_id
    issue.assigned_staff_id = staff_member.id

    try:
        if previous_staff_id != staff_member.id:
            await create_notification(
                session=session,
                recipient_id=staff_member.id,
                issue_id=issue.id,
                title="New issue assigned",
                message=f'You have been assigned the issue "{issue.title}".',
            )

        await session.commit()
        await session.refresh(issue)
    except Exception:
        await session.rollback()
        raise

    return issue


async def update_issue_status(
    session: AsyncSession,
    issue_id: UUID,
    new_status: IssueStatus,
    current_user: User,
) -> Issue:
    """Update issue status, record history, and notify its reporter."""

    issue = await get_issue_by_id(session, issue_id)

    if current_user.role == UserRole.STAFF:
        if issue.assigned_staff_id != current_user.id:
            raise IssueAccessError(
                "You can only update issues assigned to you."
            )
    elif current_user.role != UserRole.ADMIN:
        raise IssueAccessError(
            "Only staff and admins can update issue status."
        )

    allowed_statuses = _ALLOWED_TRANSITIONS.get(issue.status, set())

    if new_status not in allowed_statuses:
        raise InvalidStatusTransitionError(
            f"Cannot change status from '{issue.status}' "
            f"to '{new_status}'."
        )

    old_status = issue.status

    history_entry = IssueStatusHistory(
        issue_id=issue.id,
        changed_by_id=current_user.id,
        old_status=old_status,
        new_status=new_status,
    )

    issue.status = new_status
    session.add(history_entry)

    try:
        await create_notification(
            session=session,
            recipient_id=issue.reporter_id,
            issue_id=issue.id,
            title="Issue status updated",
            message=(
                f'Your issue "{issue.title}" changed from '
                f'"{old_status.value}" to "{new_status.value}".'
            ),
        )

        await session.commit()
        await session.refresh(issue)
    except Exception:
        await session.rollback()
        raise

    return issue
