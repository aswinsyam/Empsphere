"""
OTP Repository.

Handles MongoDB operations for one-time passwords (OTPs)
used for email verification and password reset flows.

Note: OTP documents do not use soft-delete, so these methods
query the raw collection directly (avoiding BaseRepository's
automatic `is_deleted` filter).
"""

from datetime import datetime, timezone

from bson import ObjectId

from apps.common.base.base_repository import BaseRepository
from apps.common.core.collections import Collections


class OTPRepository(BaseRepository):
    """
    Repository for the otps collection.
    """

    COLLECTION_NAME = Collections.OTPS

    def __init__(self):
        super().__init__(self.COLLECTION_NAME)

    def get_by_email_and_purpose(self, email: str, purpose: str):
        """
        Get the latest active OTP for an email + purpose.
        """
        return self.collection.find_one(
            {"email": email.lower(), "purpose": purpose}
        )

    def get_active(self, email: str, purpose: str, otp_hash: str):
        """
        Get an active (unused, un-expired) OTP matching email/purpose/hash.
        """
        return self.collection.find_one(
            {
                "email": email.lower(),
                "purpose": purpose,
                "otp_hash": otp_hash,
                "is_used": False,
                "expires_at": {"$gt": datetime.now(timezone.utc)},
            }
        )

    def mark_used(self, otp_id: str) -> bool:
        """
        Mark an OTP as used.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(otp_id)},
            {"$set": {"is_used": True}},
        )
        return result.modified_count > 0
