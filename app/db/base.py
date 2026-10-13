from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Import models so Alembic can discover their tables.
from app.models.user import User  # noqa: E402, F401