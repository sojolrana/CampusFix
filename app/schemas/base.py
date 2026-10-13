
from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """Provide common validation rules for API schemas."""

    model_config = ConfigDict(extra="forbid")


class ORMReadSchema(SchemaBase):
    """Allow response schemas to read attributes from ORM objects."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )
