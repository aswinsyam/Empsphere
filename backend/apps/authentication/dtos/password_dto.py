"""
Password Management DTOs.

Consolidated data transfer objects for all password flows:
change-password, forgot-password, reset-password, and set-password.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChangePasswordDTO:
    """DTO for an authenticated password change."""

    old_password: str
    new_password: str
    user_id: str | None = None


@dataclass
class ForgotPasswordDTO:
    """DTO for requesting a password reset email."""

    email: str


@dataclass
class ResetPasswordDTO:
    """DTO for setting a new password with a reset token."""

    token: str
    new_password: str


@dataclass
class SetPasswordDTO:
    """DTO for a Google-authenticated user setting a local password."""

    user_id: str
    otp: str
    new_password: str