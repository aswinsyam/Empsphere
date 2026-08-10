"""
JWT access and refresh token creation/verification.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from apps.common.config.settings import settings


class JWTManager:
    """Creates and validates JWT tokens."""

    @staticmethod
    def _payload(user, token_type: str) -> dict:
        now = datetime.now(timezone.utc)

        if token_type == "access":
            exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXP_MINUTES)
        else:
            exp = now + timedelta(days=settings.REFRESH_TOKEN_EXP_DAYS)

        return {
            "user_id": str(user.get("_id")),
            "email": user.get("email"),
            "role": user.get("role"),
            "token_type": token_type,
            "jti": str(uuid4()),
            "exp": exp,
            "iat": now,
        }

    @classmethod
    def generate_access_token(cls, user) -> str:
        return jwt.encode(
            cls._payload(user, "access"),
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def generate_refresh_token(cls, user) -> str:
        return jwt.encode(
            cls._payload(user, "refresh"),
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a token. Raises jwt exceptions on failure."""
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
