"""
OTP Services.

Business logic for one-time password flows:
send-otp (email verification / password reset / password setup / login) and verify-otp.
"""

from datetime import datetime, timezone

from apps.authentication.dtos.otp_dto import SendOTPDTO, VerifyOTPDTO
from apps.common.security.jwt_manager import JWTManager
from apps.authentication.managers.otp_manager import OTPManager
from apps.authentication.repositories.otp_repository import OTPRepository
from apps.authentication.repositories.user_repository import UserRepository
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    UnauthorizedException,
)


class SendOTPService:
    """Generates and emails an OTP for a given purpose."""

    def __init__(self):
        self.otp_manager = OTPManager()
        self.user_repository = UserRepository()

    def send(self, dto: SendOTPDTO) -> None:
        """
        Send an OTP to the user's email.

        For email_verification we always go through the OTP flow regardless
        of whether the account exists (to avoid leaking which emails exist).
        For password_reset we only send if the account exists (but respond
        identically regardless).

        For password_setup the email is taken from the authenticated user
        (never from the request body). Only Google-authenticated users
        without a local password may request a password-setup OTP.
        """
        if dto.purpose in ["password_reset", "login"]:
            user = self.user_repository.get_by_email(dto.email)
            if not user:
                # Do not reveal whether the email exists.
                return

        if dto.purpose == "password_setup":
            user = self.user_repository.get_by_email(dto.email)
            if not user:
                raise UnauthorizedException("User not found.")

            if user.get("login_provider") != "GOOGLE":
                raise ConflictException(
                    "Password setup is only available for Google accounts."
                )

            if user.get("password") is not None:
                raise ConflictException("A password is already set for this account.")

        self.otp_manager.create_and_send(dto.email, dto.purpose)


class VerifyOTPService(BaseService):
    """Validates an OTP and marks the user's email verified if applicable."""

    def __init__(self):
        super().__init__()
        self.otp_manager = OTPManager()
        self.otp_repository = OTPRepository()
        self.user_repository = UserRepository()

    def verify(self, dto: VerifyOTPDTO) -> dict:
        """
        Check the OTP. If valid and the purpose is email_verification,
        mark the user's email as verified. If the purpose is login,
        return JWT tokens for authentication.
        """
        otp_hash = self.otp_manager.hash_otp(dto.otp)

        otp_doc = self.otp_repository.get_active(
            dto.email, dto.purpose, otp_hash
        )

        if not otp_doc:
            raise UnauthorizedException("Invalid or expired OTP.")

        self.otp_repository.mark_used(str(otp_doc["_id"]))

        if dto.purpose == "email_verification":
            user = self.user_repository.get_by_email(dto.email)
            if user:
                self.user_repository.update(
                    str(user["_id"]),
                    {"is_email_verified": True},
                    user_id=str(user["_id"]),
                )
            return {}

        if dto.purpose == "login":
            user = self.user_repository.get_by_email(dto.email)
            if not user:
                raise UnauthorizedException("User not found.")

            # Generate JWT tokens
            jwt_manager = JWTManager()
            access_token = jwt_manager.generate_access_token(user)
            refresh_token = jwt_manager.generate_refresh_token(user)

            # Update last_login
            self.user_repository.update(
                str(user["_id"]),
                {"last_login": datetime.utcnow()},
            )

            # Log activity
            self.log_activity(
                module="AUTHENTICATION",
                action="LOGIN",
                performed_by=str(user["_id"]),
                target_id=str(user["_id"]),
                status="SUCCESS",
                description="User logged in via OTP",
            )

            return {
                "user_id": str(user["_id"]),
                "email": user.get("email"),
                "role": user.get("role"),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

        return {}
