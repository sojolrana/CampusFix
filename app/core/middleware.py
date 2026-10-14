
"""HTTP middleware for request tracing and access logging."""

import logging
import re
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import request_id_context


logger = logging.getLogger("campusfix.http")

_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a safe request ID and log request outcomes."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """Process a request while tracking its duration and outcome."""

        supplied_id = request.headers.get("X-Request-ID", "")

        if _VALID_REQUEST_ID.fullmatch(supplied_id):
            request_id = supplied_id
        else:
            request_id = str(uuid4())

        context_token = request_id_context.set(request_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "request_completed method=%s path=%s status=%s duration_ms=%s request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request_id,
            )

            return response
        except Exception:
            logger.exception(
                "request_failed method=%s path=%s request_id=%s",
                request.method,
                request.url.path,
                request_id,
            )
            raise
        finally:
            request_id_context.reset(context_token)
