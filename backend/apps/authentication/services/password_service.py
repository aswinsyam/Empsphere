"""
Password Management Services.

Consolidated business logic for all password flows:
change-password, forgot-password, and reset-password.
"""

import jwt
from datetime import datetime, timedelta, timezone

from apps.authentication.dtos.password_dto import (
    ChangePasswordDTO,
    ForgotPasswordDTO,
    ResetPasswordDTO,
    SetPasswordDTO,
)
from apps.authentication.managers.email_manager import EmailManager
from apps.authentication.managers.otp_manager import OTPManager
from apps.common.security.password_manager import PasswordManager
from apps.authentication.repositories.otp_repository import OTPRepository
from apps.authentication.repositories.user_repository import UserRepository
from apps.common.config.settings import settings
from apps.common.exceptions.custom_exception import (
    ConflictException,
    UnauthorizedException,
)


class ChangePasswordService:
    """Changes the current user's password."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()

    def change_password(self, dto: ChangePasswordDTO) -> None:
        """Verify the old password and set the new one."""

        user = self.user_repository.get_by_id(dto.user_id)

        if not user:
            raise UnauthorizedException("User not found.")

        if not self.password_manager.verify_password(
            dto.old_password, user.get("password")
        ):
            raise UnauthorizedException("Current password is incorrect.")

        hashed = self.password_manager.hash_password(dto.new_password)

        self.user_repository.update(
            dto.user_id,
            {"password": hashed},
            user_id=dto.user_id,
        )


class ForgotPasswordService:
    """Generates a reset token and emails it to the user."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.email_manager = EmailManager()

    def forgot_password(self, dto: ForgotPasswordDTO) -> None:
        """Send a password reset email if the account exists."""

        user = self.user_repository.get_by_email(dto.email)

        if not user:
            # Do not reveal whether the email exists.
            return

        payload = {
            "user_id": str(user["_id"]),
            "token_type": "password_reset",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        self.email_manager.send_forgot_password_email(dto.email, token)


class ResetPasswordService:
    """Sets a new password from a reset token."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()

    def reset_password(self, dto: ResetPasswordDTO) -> None:
        """Validate the reset token and update the password."""

        try:
            payload = jwt.decode(
                dto.token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError:
            raise UnauthorizedException("The reset token is invalid or has expired.")

        if payload.get("token_type") != "password_reset":
            raise UnauthorizedException("Invalid token type.")

        user_id = payload.get("user_id")

        if not user_id:
            raise UnauthorizedException("Invalid token payload.")

        # Ensure the user still exists before updating.
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found.")

        hashed = self.password_manager.hash_password(dto.new_password)

        self.user_repository.update(
            user_id,
            {"password": hashed},
            user_id=user_id,
        )


class SetPasswordService:
    """
    Sets a local password for a Google-authenticated user.

    Flow:
      1. The authenticated Google user requests an OTP with
         purpose="password_setup" (email comes from the session).
      2. The user submits the OTP plus a new password.
      3. The OTP is verified against the user's verified email.
      4. The new password is hashed and stored.

    The identity is enforced by the backend via the access token —
    the frontend cannot choose which email receives the OTP.
    """

    def __init__(self):
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()
        self.otp_manager = OTPManager()
        self.otp_repository = OTPRepository()

    def set_password(self, dto: SetPasswordDTO) -> None:
        """Verify the OTP and set the new password for the authenticated user."""

        user = self.user_repository.get_by_id(dto.user_id)

        if not user:
            raise UnauthorizedException("User not found.")

        if user.get("login_provider") != "GOOGLE":
            raise ConflictException(
                "Password setup is only available for Google accounts."
            )

        if user.get("password") is not None:
            raise ConflictException("A password is already set for this account.")

        # Verify the OTP for this user's verified email.
        otp_hash = self.otp_manager.hash_otp(dto.otp)

        otp_doc = self.otp_repository.get_active(
            user.get("email"), "password_setup", otp_hash
        )

        if not otp_doc:
            raise UnauthorizedException("Invalid or expired OTP.")

        self.otp_repository.mark_used(str(otp_doc["_id"]))

        hashed = self.password_manager.hash_password(dto.new_password)

        self.user_repository.update(
            dto.user_id,
            {"password": hashed},
            user_id=dto.user_id,
        )
