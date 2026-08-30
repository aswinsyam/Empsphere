"""
Secure password hashing and verification.
"""

from passlib.context import CryptContext

# Use bcrypt for compatibility. Enforce a UTF-8 byte-length check to
# prevent runtime errors from bcrypt's 72-byte limit — callers will get a
# clear ValidationException if a password is too long.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    """Handles password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password."""
        try:
            b = password.encode("utf-8") if isinstance(password, str) else bytes(password)
        except Exception:
            b = None

        if b is not None and len(b) > 72:
            from apps.common.exceptions.custom_exception import ValidationException

            raise ValidationException(
                message="Password must be at most 72 bytes when UTF-8 encoded."
            )

        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a stored bcrypt hash.

        A stored value that is not a recognizable bcrypt hash (e.g. a legacy
        plaintext value or a hash produced by a different algorithm) can
        never validate a password. Returning False here converts what would
        otherwise surface as an unhandled ``UnknownHashError`` (HTTP 500)
        into a clean "invalid credentials" result (HTTP 401), instead of
        leaking an internal exception.
        """
        if not hashed_password:
            return False
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except (ValueError, TypeError):
            return False
