
"""In-memory rate limiting for selected API endpoints."""

import asyncio
import time
from collections import defaultdict

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit request frequency for selected endpoints and client IPs."""

    def __init__(self, app) -> None:
        """Initialize endpoint limits and in-memory request counters."""
        super().__init__(app)
        self._limits: dict[str, tuple[int, int]] = {
            "/api/v1/auth/login": (10, 60),
            "/api/v1/users": (5, 60),
            "/api/v1/issues": (20, 60),
        }
        self._requests: dict[tuple[str, str], list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Reject requests that exceed their endpoint's allowed rate."""
        if request.method != "POST":
            return await call_next(request)

        limit_config = self._limits.get(request.url.path)
        if limit_config is None:
            return await call_next(request)

        limit, window_seconds = limit_config
        client_host = (
            request.client.host
            if request.client is not None
            else "unknown"
        )
        key = (request.url.path, client_host)
        now = time.monotonic()

        async with self._lock:
            timestamps = self._requests[key]
            timestamps[:] = [
                timestamp
                for timestamp in timestamps
                if now - timestamp < window_seconds
            ]

            if len(timestamps) >= limit:
                retry_after = max(
                    1,
                    int(window_seconds - (now - timestamps[0])),
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again later."
                    },
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)

        return await call_next(request)
