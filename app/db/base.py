"""Define the SQLAlchemy declarative base for database models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Provide the common base class for all SQLAlchemy ORM models."""