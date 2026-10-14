
"""Create the CampusFix FastAPI application."""

import logging
import os

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.responses import Response
from starlette.middleware.base import RequestResponseEndpoint

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.db.session import engine
from app.middleware.request_context import RequestContextMiddleware


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    description="Campus issue reporting and resolution platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Add baseline security headers to HTTP responses."""
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


app.add_middleware(RequestContextMiddleware)
register_error_handlers(app)

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


@app.get("/ready", tags=["Health"])
async def readiness_check() -> dict[str, str]:
    """Check whether the API can reach its PostgreSQL database."""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The application is not ready.",
        ) from exc

    return {
        "status": "ready",
        "database": "connected",
    }
