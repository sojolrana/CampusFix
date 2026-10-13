
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import EmailStr, Field, StringConstraints

from app.enums.user_role import UserRole
from app.schemas.base import ORMReadSchema, SchemaBase


class UserCreate(SchemaBase):
    """Validate the data required to register a new user."""

    full_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=2,
            max_length=100,
        ),
    ]

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
        repr=False,
    )


class UserRead(ORMReadSchema):
    """Define the user information that the API may return."""

    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
