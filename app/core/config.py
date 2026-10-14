
"""Application settings and environment configuration validation."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load and validate application settings from environment variables."""

    app_name: str = "CampusFix"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        """Normalize the environment and reject unsupported values."""
        normalized = value.strip().lower()
        allowed_environments = {
            "development",
            "testing",
            "production",
        }

        if normalized not in allowed_environments:
            raise ValueError(
                "APP_ENV must be development, testing, or production."
            )

        return normalized

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, origins: list[str]) -> list[str]:
        """Normalize origins and reject empty or malformed entries."""
        cleaned_origins = list(
            dict.fromkeys(origin.strip().rstrip("/") for origin in origins)
        )

        if any(not origin for origin in cleaned_origins):
            raise ValueError("CORS origins must not contain empty entries.")

        for origin in cleaned_origins:
            if origin != "*" and not origin.startswith(("http://", "https://")):
                raise ValueError(
                    "Each CORS origin must start with http:// or https://."
                )

        return cleaned_origins

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Reject unsafe debug settings, weak secrets, and wildcard CORS."""
        if self.app_env != "production":
            return self

        if self.debug:
            raise ValueError("DEBUG must be false in production.")

        secret = self.jwt_secret_key.strip()
        normalized_secret = secret.lower()

        if len(secret) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must contain at least 32 characters "
                "in production."
            )

        placeholder_markers = (
            "replace_with",
            "change_me",
            "your_secret",
            "example_secret",
        )
        known_weak_secrets = {
            "changeme",
            "change-me",
            "secret",
            "your-secret-key",
        }

        if (
            normalized_secret in known_weak_secrets
            or any(marker in normalized_secret for marker in placeholder_markers)
        ):
            raise ValueError(
                "Replace the placeholder JWT_SECRET_KEY "
                "with a unique random secret."
            )

        if "*" in self.cors_origins:
            raise ValueError(
                "Wildcard CORS origins are not allowed in production."
            )

        if any(origin.startswith("http://") for origin in self.cors_origins):
            raise ValueError(
                "Production CORS origins must use HTTPS."
            )

        return self


settings = Settings()
