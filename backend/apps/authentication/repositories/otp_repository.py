"""
OTP Repository.
Handles OTP database operations.
"""
from __future__ import annotations

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class OTPRepository:
    """OTP data access layer."""

    def get_active(self, email, purpose):
        """Get active OTP for email and purpose."""
        collection = mongo.get_collection(Collections.OTPS)
        return collection.find_one({
            "email": email,
            "purpose": purpose,
            "is_used": False,
        })

    def create(self, document):
        """Create a new OTP record."""
        collection = mongo.get_collection(Collections.OTPS)
        return collection.insert_one(document).inserted_id

    def mark_used(self, otp_id):
        """Mark OTP as used."""
        collection = mongo.get_collection(Collections.OTPS)
        collection.update_one({"_id": otp_id}, {"$set": {"is_used": True}})

    def invalidate_active(self, email, purpose):
        """Invalidate existing active OTPs."""
        collection = mongo.get_collection(Collections.OTPS)
        collection.update_many(
            {"email": email, "purpose": purpose, "is_used": False},
            {"$set": {"is_used": True}},
        )