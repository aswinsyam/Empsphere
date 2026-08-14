"""
OTP Service.
Handles OTP creation and verification.
"""
from __future__ import annotations

from apps.authentication.repositories.otp_repository import OTPRepository
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import NotFoundException


class OTPService(BaseService):
    """OTP business logic."""

    def __init__(self):
        super().__init__()
        self.otp_repository = OTPRepository()

    def send_otp(self, dto):
        """Send OTP to user email."""
        email = dto.get("email")
        purpose = dto.get("purpose", "email_verification")
        # Invalidate existing OTPs for this email and purpose
        self.otp_repository.invalidate_active(email, purpose)
        # Generate and store new OTP
        import random
        otp_code = str(random.randint(100000, 999999))
        self.otp_repository.create({
            "email": email,
            "purpose": purpose,
            "otp": otp_code,
            "expires_at": self._get_expiry_time(),
            "is_used": False,
        })
        return {
            "message": f"OTP sent to {email}",
            "otp_purpose": purpose,
        }

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
        if self._is_expired(otp_record.get("expires_at")):
            raise NotFoundException("OTP expired.")
        # Mark as used
        self.otp_repository.mark_used(otp_record["_id"])
        return {
            "message": "OTP verified successfully.",
            "verified": True,
        }

    def _get_expiry_time(self):
        """Get OTP expiry time."""
        from datetime import datetime, timedelta
        return datetime.utcnow() + timedelta(minutes=10)

    def _is_expired(self, expires_at):
        """Check if OTP has expired."""
        from datetime import datetime
        return datetime.utcnow() > expires_at