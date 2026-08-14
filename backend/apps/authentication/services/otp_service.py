"""
OTP Service.
Handles OTP creation, verification, and email delivery.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.authentication.repositories.otp_repository import OTPRepository
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import NotFoundException


class OTPService(BaseService):
    """OTP business logic."""

    def __init__(self):
        super().__init__()
        self.otp_repository = OTPRepository()

    def send_otp(self, dto):
        """Send OTP to user email and deliver via SMTP."""
        email = dto.get("email")
        purpose = dto.get("purpose", "email_verification")
        self.otp_repository.invalidate_active(email, purpose)
        otp_code = str(random.randint(100000, 999999))
        self.otp_repository.create({
            "email": email,
            "purpose": purpose,
            "otp": otp_code,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "is_used": False,
        })
        self._send_otp_email(email, otp_code, purpose)
        return {
            "message": f"OTP sent to {email}",
            "otp_purpose": purpose,
        }

    def _send_otp_email(self, email, otp_code, purpose):
        """Render the OTP email template and send it via Django SMTP."""
        subject = "EmpSphere OTP Code"
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
            fail_silently=True,
        )

    def verify_otp(self, dto):
        """Verify OTP code."""
        email = dto.get("email")
        otp_code = dto.get("otp")
        purpose = dto.get("purpose", "email_verification")
        otp_record = self.otp_repository.get_active(email, purpose)
        if not otp_record:
            raise NotFoundException("OTP not found or expired.")
        if otp_record.get("is_used"):
            raise NotFoundException("OTP already used.")
        if otp_record.get("otp") != otp_code:
            raise NotFoundException("Invalid OTP code.")
        if datetime.utcnow() > otp_record.get("expires_at"):
            raise NotFoundException("OTP expired.")
        self.otp_repository.mark_used(otp_record["_id"])
        return {
            "message": "OTP verified successfully.",
            "verified": True,
        }