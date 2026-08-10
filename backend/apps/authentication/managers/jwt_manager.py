"""
Authentication JWT manager.

Thin wrapper around the common JWT utility.
"""

from apps.common.security.jwt_manager import JWTManager as CommonJWTManager


class JWTManager:
    """JWT token utilities for the authentication module."""

    @staticmethod
    def generate_access_token(user) -> str:
        return CommonJWTManager.generate_access_token(user)

    @staticmethod
    def generate_refresh_token(user) -> str:
        return CommonJWTManager.generate_refresh_token(user)

    @staticmethod
    def decode_token(token: str) -> dict:
        return CommonJWTManager.decode_token(token)
