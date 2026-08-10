"""
OTP Manager.

Generates, hashes, validates, and stores one-time passwords (OTPs)
for email verification and password-reset flows.
"""

import secrets
from datetime import datetime, timedelta, timezone

from apps.authentication.managers.email_manager import EmailManager
from apps.authentication.repositories.otp_repository import OTPRepository
from apps.common.config.settings import settings


class OTPManager:
    """
    Manages OTP lifecycle: generate, hash, store, verify.
    """

    DEFAULT_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6

    def __init__(self):
        self.otp_repository = OTPRepository()

    # --------------------------------------------------
    # Generate
    # --------------------------------------------------

    @staticmethod
    def generate_otp(length: int = OTP_LENGTH) -> str:
        """Generate a numeric OTP of the given length."""
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    def create_and_send(
        self,
        email: str,
        purpose: str,
        expiry_minutes: int = DEFAULT_EXPIRY_MINUTES,
    ) -> str:
        """
        Generate an OTP, store it (hashed), and email it to the user.

        Returns the plaintext OTP (for logging/dev). In production the
        plaintext is only sent to the user's email.
        """
        otp = self.generate_otp()
        otp_hash = self.hash_otp(otp)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)

        document = {
            "email": email.lower(),
            "purpose": purpose,
            "otp_hash": otp_hash,
            "is_used": False,
            "expires_at": expires_at,
        }

        self.otp_repository.create(document)
        EmailManager.send_otp_email(email, otp, purpose)

        return otp

    # --------------------------------------------------
    # Hash
    # --------------------------------------------------

    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash an OTP using SHA-256 with a per-OTP secret suffix."""
        import hashlib

        return hashlib.sha256(f"{otp}:{settings.JWT_SECRET}".encode()).hexdigest()

    @staticmethod
    def verify_otp(otp: str, otp_hash: str) -> bool:
        """Compare a plaintext OTP against a stored hash."""
        import hashlib

        return hashlib.sha256(f"{otp}:{settings.JWT_SECRET}".encode()).hexdigest() == otp_hash
