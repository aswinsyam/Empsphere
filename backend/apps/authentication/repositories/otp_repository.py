"""
OTP Repository.
Handles OTP database operations.
"""
from __future__ import annotations

from datetime import datetime

from bson import ObjectId

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
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def mark_used(self, otp_id):
        """Atomically mark an OTP as used.

        Returns ``True`` only for the caller that transitioned the record
        from unused to used, so a single OTP can never be consumed twice
        (even by concurrent requests).
        """
        collection = mongo.get_collection(Collections.OTPS)
        result = collection.update_one(
            {"_id": ObjectId(otp_id), "is_used": False},
            {"$set": {"is_used": True, "used_at": datetime.utcnow()}},
        )
        return result.modified_count == 1

    def invalidate_active(self, email, purpose):
        """Invalidate existing active OTPs."""
        collection = mongo.get_collection(Collections.OTPS)
        collection.update_many(
            {"email": email, "purpose": purpose, "is_used": False},
            {"$set": {"is_used": True, "used_at": datetime.utcnow()}},
        )