"""Pydantic schemas for authentication responses."""

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    """Define the access token returned after successful login."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(repr=False)
    token_type: str = "bearer"