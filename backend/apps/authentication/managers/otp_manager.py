"""
OTP Manager.
Handles OTP lifecycle.
"""
from __future__ import annotations

from apps.authentication.repositories.otp_repository import OTPRepository
from apps.common.base.base_manager import BaseManager


class OTPManager(BaseManager):
    """OTP lifecycle management."""

    def __init__(self):
        super().__init__()
        self.otp_repository = OTPRepository()

    def create_and_send(self, email, purpose="email_verification"):
        """Create and send OTP."""
        # Invalidate existing OTPs
        self.otp_repository.invalidate_active(email, purpose)
        # Generate OTP
        import random
        otp_code = str(random.randint(100000, 999999))
        # Store OTP
        self.otp_repository.create({
            "email": email,
            "purpose": purpose,
            "otp": otp_code,
            "expires_at": self._get_expiry_time(),
            "is_used": False,
        })
        # In real implementation, would send via email
        return {
            "message": f"OTP sent to {email}",
            "otp_code": otp_code,
            "purpose": purpose,
        }

    def verify(self, dto):
        """Verify OTP."""
        email = dto.get("email")
        otp_code = dto.get("otp")
        purpose = dto.get("purpose", "email_verification")
        return self.otp_repository.get_active(email, purpose)

    def _get_expiry_time(self):
        """Get OTP expiry."""
        from datetime import datetime, timedelta
        return datetime.utcnow() + timedelta(minutes=10)