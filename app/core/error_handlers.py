
"""Centralized HTTP and validation error handlers."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.request_context import request_id_context


logger = logging.getLogger("campusfix.errors")


def _error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """Build the standard JSON response used for API errors."""

    content: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

    if details is not None:
        content["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register centralized handlers for common API exceptions."""

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Return a consistent response for expected HTTP errors."""

        request_id = request_id_context.get()

        messages = {
            400: ("BAD_REQUEST", "The request could not be processed."),
            401: ("UNAUTHORIZED", "Authentication is required."),
            403: ("FORBIDDEN", "You do not have permission to perform this action."),
            404: ("NOT_FOUND", "The requested resource was not found."),
            409: ("CONFLICT", "The request conflicts with the current resource state."),
            422: ("VALIDATION_ERROR", "The request data is invalid."),
            429: ("RATE_LIMITED", "Too many requests."),
        }

        code, default_message = messages.get(
            exc.status_code,
            ("HTTP_ERROR", "The request could not be completed."),
        )

        message = exc.detail if isinstance(exc.detail, str) else default_message

        return _error_response(
            status_code=exc.status_code,
            code=code,
            message=message,
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return field-level details for invalid request data."""

        details = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]

        return _error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="The request data is invalid.",
            request_id=request_id_context.get(),
            details=details,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Log unexpected exceptions and return a generic server error."""

        request_id = request_id_context.get()

        logger.exception(
            "unhandled_exception method=%s path=%s request_id=%s",
            request.method,
            request.url.path,
            request_id,
            exc_info=(type(exc), exc, exc.__traceback__),
        )

        return _error_response(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred.",
            request_id=request_id,
        )
