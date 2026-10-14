
"""Middleware for request tracing and HTTP request logging."""

import logging
import re
import time
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.core.request_context import request_id_context

logger = logging.getLogger(__name__)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID, log request outcomes, and return the ID in headers."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process a request and record its duration and response status."""
        supplied_request_id = request.headers.get("X-Request-ID", "")

        if REQUEST_ID_PATTERN.fullmatch(supplied_request_id):
            request_id = supplied_request_id
        else:
            request_id = str(uuid4())

        context_token = request_id_context.set(request_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "Request completed method=%s path=%s status=%s "
                "duration_ms=%.2f request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request_id,
            )

            return response

        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.exception(
                "Request failed method=%s path=%s duration_ms=%.2f "
                "request_id=%s",
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise

        finally:
            request_id_context.reset(context_token)
