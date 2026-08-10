"""
Authentication email manager.

Sends authentication related emails (verification, password reset, OTP).
"""

from datetime import datetime

from apps.common.config.settings import settings
from apps.common.email.email_service import EmailService
from apps.common.email.email_templates import EmailTemplates


class EmailManager:
    """Composes and sends authentication emails."""

    @staticmethod
    def send_verification_email(to_email: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        EmailService.send(
            subject="Verify your email",
            to_emails=[to_email],
            template_name=EmailTemplates.VERIFY_EMAIL,
            context={"link": link},
        )

    @staticmethod
    def send_forgot_password_email(to_email: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        EmailService.send(
            subject="Reset your password",
            to_emails=[to_email],
            template_name=EmailTemplates.FORGOT_PASSWORD,
            context={"link": link},
        )

    @staticmethod
    def send_otp_email(to_email: str, otp: str, purpose: str = "email_verification") -> None:
        """Send a one-time password (OTP) to the user's email."""
        subject_map = {
            "email_verification": "Your verification code",
            "password_reset": "Your password reset code",
            "password_setup": "Your password setup code",
            "login": "Your login code",
        }
        subject = subject_map.get(purpose, "Your EmpSphere OTP code")

        EmailService.send(
            subject=subject,
            to_emails=[to_email],
            template_name=EmailTemplates.OTP,
            context={"otp": otp, "purpose": purpose, "year": datetime.now().year},
        )