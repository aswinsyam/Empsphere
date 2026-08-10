"""
Authentication password manager.

Thin wrapper around the common password hashing utility.
"""

from apps.common.security.password_manager import PasswordManager as CommonPasswordManager


class PasswordManager:
    """Password utilities for the authentication module."""

    @staticmethod
    def hash_password(password: str) -> str:
        return CommonPasswordManager.hash_password(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return CommonPasswordManager.verify_password(plain_password, hashed_password)
