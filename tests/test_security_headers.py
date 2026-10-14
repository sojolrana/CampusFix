
"""Tests for baseline HTTP security headers."""

from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_are_added() -> None:
    """Verify that baseline security headers are returned."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert (
        response.headers["Referrer-Policy"]
        == "strict-origin-when-cross-origin"
    )
