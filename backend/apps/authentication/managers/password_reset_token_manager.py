"""
Password Reset Token Manager.

Issues and validates the short-lived, single-use authorization token that
is handed out **after** a ``forgot_password`` OTP has been verified. The
token is the only thing that authorizes the reset-password endpoint; it
never authenticates a request (``token_type`` is not ``access``, so
``JWTAuthentication`` rejects it).

Single-use is enforced with the existing token blacklist infrastructure.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import jwt

from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
from apps.common.base.base_manager import BaseManager
from apps.common.config.settings import settings
from apps.common.core.otp import OTPPurpose
from apps.common.exceptions.custom_exception import (
    InternalServerException,
    UnauthorizedException,
)

#: Token type claim used by password reset tokens.
TOKEN_TYPE = "password_reset"


class PasswordResetTokenManager(BaseManager):
    """Password reset authorization token management."""

    def __init__(self):
        super().__init__()
        self.token_blacklist_manager = TokenBlacklistManager()

    def generate(self, user):
        """Issue a short-lived, purpose-specific password reset token."""
        issued_at = datetime.utcnow()
        return jwt.encode(
            {
                "user_id": str(user["_id"]),
                "email": user.get("email"),
                "purpose": OTPPurpose.FORGOT_PASSWORD,
                "token_type": TOKEN_TYPE,
                "jti": uuid.uuid4().hex,
                "iat": issued_at,
                "exp": issued_at + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXP_MINUTES),
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    def verify(self, reset_token):
        """Validate a reset token and return its payload.

        Rejects tokens that are missing, already used, expired, tampered
        with, or issued for any other purpose/token type.
        """
        if not reset_token:
            raise UnauthorizedException("Password reset token is required.")

        if self.token_blacklist_manager.is_blacklisted(reset_token):
            raise UnauthorizedException(
                "This password reset token has already been used. Please request a new OTP."
            )

        try:
            payload = jwt.decode(
                reset_token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException(
                "Password reset token has expired. Please request a new OTP."
            )
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid password reset token.")

        if payload.get("token_type") != TOKEN_TYPE:
            raise UnauthorizedException("Invalid password reset token.")

        if payload.get("purpose") != OTPPurpose.FORGOT_PASSWORD:
            raise UnauthorizedException("Invalid password reset token.")

        if not payload.get("user_id"):
            raise UnauthorizedException("Invalid password reset token.")

        return payload

    def invalidate(self, reset_token):
        """Consume a reset token so it can never be used again.

        Fails closed: if the token cannot be recorded as used, the reset
        must not continue.
        """
        if not self.token_blacklist_manager.blacklist(reset_token):
            raise InternalServerException(
                "Could not complete the password reset. Please request a new OTP."
            )
