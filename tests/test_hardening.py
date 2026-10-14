
"""Tests for request tracing, error formatting, and readiness."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_success() -> None:
    """Verify that the basic health endpoint responds successfully."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200


def test_request_id_is_returned() -> None:
    """Verify that requests receive a response request ID."""
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "campusfix-test-123"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "campusfix-test-123"


def test_invalid_request_returns_standard_error() -> None:
    """Verify that request validation uses the standard error format."""
    with TestClient(app) as client:
        response = client.get("/health", params={"unexpected": "value"})

    # The health endpoint may ignore unknown query parameters.
    # Use an unauthenticated login request with a missing required field
    # to exercise request-body validation before authentication.
    if response.status_code != 422:
        with TestClient(app) as client:
            response = client.post("/api/v1/auth/login", json={})

    assert response.status_code == 422

    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in body["error"]
    assert isinstance(body["error"]["details"], list)


def test_readiness_endpoint() -> None:
    """Verify that readiness reports a healthy database connection."""
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }
