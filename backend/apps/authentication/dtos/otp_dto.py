"""
OTP DTOs.

Data transfer objects for one-time password flows
(email verification and password reset).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SendOTPDTO:
    """Represents a request to send an OTP to an email."""

    email: str
    purpose: str = "email_verification"


@dataclass
class VerifyOTPDTO:
    """Represents a request to verify an OTP."""

    email: str
    otp: str
    purpose: str = "email_verification"
