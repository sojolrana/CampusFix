"""Create the CampusFix FastAPI application."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    description="Campus issue reporting and resolution platform.",
)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Return basic information about the CampusFix API."""
    return {
        "message": "Welcome to CampusFix API",
        "application": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {
        "status": "healthy",
        "application": settings.app_name,
    }