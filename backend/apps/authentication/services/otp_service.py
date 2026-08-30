"""
OTP Service.
Handles OTP creation, verification, and email delivery.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.authentication.repositories.otp_repository import OTPRepository
from apps.common.base.base_service import BaseService
from apps.common.core.otp import OTPPurpose, OTP_EXPIRY_MINUTES, OTP_LENGTH
from apps.common.exceptions.custom_exception import NotFoundException


class OTPService(BaseService):
    """OTP business logic."""

    #: Purpose-specific email subjects (falls back to the generic subject).
    EMAIL_SUBJECTS = {
        OTPPurpose.FORGOT_PASSWORD: "EmpSphere Password Reset Code",
    }
    DEFAULT_EMAIL_SUBJECT = "EmpSphere OTP Code"

    def __init__(self):
        super().__init__()
        self.otp_repository = OTPRepository()

    def send_otp(self, dto):
        """Send OTP to user email and deliver via SMTP."""
        email = dto.get("email")
        purpose = dto.get("purpose", OTPPurpose.DEFAULT)
        self.otp_repository.invalidate_active(email, purpose)
        otp_code = self._generate_otp()
        self.otp_repository.create({
            "email": email,
            "purpose": purpose,
            "otp": otp_code,
            "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
            "is_used": False,
            "created_at": datetime.utcnow(),
        })
        self._send_otp_email(email, otp_code, purpose)
        return {
            "message": f"OTP sent to {email}",
            "otp_purpose": purpose,
        }

    @staticmethod
    def _generate_otp():
        """Generate a cryptographically secure numeric OTP code."""
        upper_bound = 10 ** OTP_LENGTH
        lower_bound = 10 ** (OTP_LENGTH - 1)
        return str(secrets.randbelow(upper_bound - lower_bound) + lower_bound)

    def _send_otp_email(self, email, otp_code, purpose):
        """Render the OTP email template and send it via Django SMTP."""
        subject = self.EMAIL_SUBJECTS.get(purpose, self.DEFAULT_EMAIL_SUBJECT)
        context = {
            "otp": otp_code,
            "year": datetime.utcnow().year,
            "purpose": purpose,
        }
        html_message = None
        try:
            html_message = render_to_string("emails/otp_email.html", context)
        except Exception:
            pass
        send_mail(
            subject=subject,
            message=f"Your OTP code is: {otp_code}",
            from_email=None,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

    def invalidate_otps(self, email, purpose):
        """Invalidate every active OTP issued for an email and purpose."""
        self.otp_repository.invalidate_active(email, purpose)

    def verify_otp(self, dto):
        """Verify OTP code for the requested email and purpose.

        An OTP only matches when it was issued for the same email *and*
        the same purpose, has not expired, and has not been used yet.
        """
        email = dto.get("email")
        otp_code = dto.get("otp")
        purpose = dto.get("purpose", OTPPurpose.DEFAULT)
        otp_record = self.otp_repository.get_active(email, purpose)
        if not otp_record:
            raise NotFoundException("OTP not found or expired.")
        if otp_record.get("is_used"):
            raise NotFoundException("OTP already used.")
        if otp_record.get("otp") != otp_code:
            raise NotFoundException("Invalid OTP code.")
        if datetime.utcnow() > otp_record.get("expires_at"):
            raise NotFoundException("OTP expired.")
        if not self.otp_repository.mark_used(otp_record["_id"]):
            # Another request consumed the same OTP first.
            raise NotFoundException("OTP already used.")
        return {
            "message": "OTP verified successfully.",
            "verified": True,
        }
