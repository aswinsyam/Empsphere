"""
OTP DTOs.
Data transfer objects for OTP.
"""
from __future__ import annotations


class SendOTPDTO:
    """Send OTP data transfer object."""

    def __init__(self, email, purpose="email_verification"):
        self.email = email
        self.purpose = purpose

    def get(self, key, default=None):
        return getattr(self, key, default)


class VerifyOTPDTO:
    """Verify OTP data transfer object."""

    def __init__(self, email, otp, purpose="email_verification"):
        self.email = email
        self.otp = otp
        self.purpose = purpose

    def get(self, key, default=None):
        return getattr(self, key, default)