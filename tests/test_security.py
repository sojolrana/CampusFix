"""Tests for password hashing and verification."""

from app.core.security import hash_password, verify_password


def test_hash_password_does_not_return_plaintext() -> None:
    """Ensure password hashing does not return the original password."""
    password = "CampusFix-Test-2026!"
    hashed_password = hash_password(password)

    assert hashed_password != password


def test_verify_password_accepts_correct_password() -> None:
    """Accept the original password when compared with its hash."""
    password = "CampusFix-Test-2026!"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_rejects_incorrect_password() -> None:
    """Reject a password that does not match the stored hash."""
    hashed_password = hash_password("CampusFix-Test-2026!")

    assert verify_password("Incorrect-Password-2026!", hashed_password) is False