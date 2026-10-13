"""Security utilities for password hashing and verification."""

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using the recommended password-hashing algorithm."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check whether a plaintext password matches a stored password hash."""
    return password_hash.verify(password, hashed_password)