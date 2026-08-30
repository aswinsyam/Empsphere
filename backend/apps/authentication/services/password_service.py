"""
Password Service.
Handles password operations.
"""
from __future__ import annotations

from apps.authentication.managers.password_reset_token_manager import PasswordResetTokenManager
from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
from apps.authentication.repositories.user_repository import UserRepository
from apps.authentication.services.otp_service import OTPService
from apps.common.base.base_service import BaseService
from apps.common.core.otp import OTPPurpose
from apps.common.security.password_manager import PasswordManager
from apps.common.exceptions.custom_exception import NotFoundException, UnauthorizedException, ValidationException


class PasswordService(BaseService):
    """Password business logic."""

    #: Returned for every forgot-password request so the API never reveals
    #: whether an account exists for the submitted email.
    FORGOT_PASSWORD_MESSAGE = "OTP sent to your email."

    #: Generic OTP failure message reused for unknown accounts so a wrong
    #: OTP and an unknown email are indistinguishable.
    OTP_FAILURE_MESSAGE = "OTP not found or expired."

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.otp_service = OTPService()
        self.password_manager = PasswordManager()
        self.reset_token_manager = PasswordResetTokenManager()
        self.token_blacklist_manager = TokenBlacklistManager()

    def hash_password(self, password):
        """Hash a password."""
        return self.password_manager.hash_password(password)

    def verify_password(self, plain_password, hashed_password):
        """Verify password."""
        return self.password_manager.verify_password(plain_password, hashed_password)

    def change_password(self, user_id, current_password, new_password):
        """Change user password after verifying current password."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        if current_password is not None:
            if not self.password_manager.verify_password(
                current_password, user.get("password")
            ):
                raise UnauthorizedException("Current password is incorrect.")
        hashed = self.password_manager.hash_password(new_password)
        self.user_repository.update(user_id, {"password": hashed})
        self.log_activity(
            module="AUTHENTICATION",
            action="PASSWORD_CHANGE",
            performed_by=user_id,
            target_id=user_id,
            status="SUCCESS",
            description="User changed their password.",
        )
        return {"message": "Password changed successfully."}

    def set_password(self, user_id, new_password):
        """Set a new password without verifying the current one."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        hashed = self.password_manager.hash_password(new_password)
        self.user_repository.update(user_id, {"password": hashed})
        self.log_activity(
            module="AUTHENTICATION",
            action="PASSWORD_SET",
            performed_by=user_id,
            target_id=user_id,
            status="SUCCESS",
            description="User set their password.",
        )
        return {"message": "Password set successfully."}

    def request_password_reset(self, email):
        """Send a ``forgot_password`` OTP to a registered account.

        Nothing is sent for unknown or inactive accounts, but the caller
        always receives the same response so the endpoint cannot be used
        to enumerate accounts.
        """
        if not email:
            raise ValidationException("Email is required.")

        user = self.user_repository.get_by_email(email)
        if not user or user.get("status") == "INACTIVE":
            return {"message": self.FORGOT_PASSWORD_MESSAGE, "email_sent": False}

        self.otp_service.send_otp({
            "email": email,
            "purpose": OTPPurpose.FORGOT_PASSWORD,
        })

        self.log_activity(
            module="AUTHENTICATION",
            action="PASSWORD_RESET_REQUEST",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description="Password reset OTP requested.",
        )

        return {"message": self.FORGOT_PASSWORD_MESSAGE, "email_sent": True}

    def verify_password_reset_otp(self, email, otp):
        """Verify a ``forgot_password`` OTP and issue a reset token.

        The OTP is consumed here (single use) and the caller is **not**
        logged in: the returned token only authorizes a password reset.
        """
        self.otp_service.verify_otp({
            "email": email,
            "otp": otp,
            "purpose": OTPPurpose.FORGOT_PASSWORD,
        })

        user = self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(self.OTP_FAILURE_MESSAGE)

        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )

        reset_token = self.reset_token_manager.generate(user)

        self.log_activity(
            module="AUTHENTICATION",
            action="OTP_VERIFY",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description=f"OTP verified for purpose: {OTPPurpose.FORGOT_PASSWORD}.",
        )

        return {
            "message": "OTP verified successfully.",
            "verified": True,
            "reset_token": reset_token,
        }

    def reset_password(self, reset_token, new_password):
        """Reset a password using a verified password reset token."""
        if not new_password:
            raise ValidationException("New password is required.")

        payload = self.reset_token_manager.verify(reset_token)

        user = self.user_repository.get_by_id(payload.get("user_id"))
        if not user:
            raise NotFoundException("User not found.")

        if payload.get("email") != user.get("email"):
            raise UnauthorizedException("Invalid password reset token.")

        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )

        # Hash first (this also enforces the password length policy), then
        # consume the reset authorization *before* the password is written so
        # a token can never be replayed, even if a later step fails.
        hashed = self.password_manager.hash_password(new_password)
        self.reset_token_manager.invalidate(reset_token)
        self.user_repository.update(str(user["_id"]), {"password": hashed})

        # Drop any remaining forgot-password OTPs and existing sessions.
        self.otp_service.invalidate_otps(
            (user.get("email") or "").strip().lower(), OTPPurpose.FORGOT_PASSWORD
        )
        self.token_blacklist_manager.blacklist_all_user_tokens(str(user["_id"]))

        self.log_activity(
            module="AUTHENTICATION",
            action="PASSWORD_RESET",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description="User reset their password via OTP.",
        )

        return {"message": "Password reset successfully."}
