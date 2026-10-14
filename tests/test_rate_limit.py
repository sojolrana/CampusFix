
"""Tests for API rate limiting."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.rate_limit import RateLimitMiddleware


def create_test_app() -> FastAPI:
    """Create an isolated FastAPI application for rate-limit tests."""
    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware)

    @test_app.post("/api/v1/users")
    async def create_test_user() -> dict[str, str]:
        """Return a test response for the registration endpoint."""
        return {"status": "accepted"}

    return test_app


def test_registration_is_rate_limited() -> None:
    """Verify that excess registration requests receive HTTP 429."""
    test_app = create_test_app()

    with TestClient(test_app) as client:
        responses = [
            client.post("/api/v1/users")
            for _ in range(6)
        ]

    assert [response.status_code for response in responses] == [
        200, 200, 200, 200, 200, 429
    ]
    assert responses[-1].headers["Retry-After"]
    assert "Too many requests" in responses[-1].json()["detail"]
