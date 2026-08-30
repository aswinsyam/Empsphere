"""
User Schema.
MongoDB schema definitions for user.
"""
from __future__ import annotations

import re

from bson import ObjectId
from datetime import datetime

from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class UserSchema:
    """User MongoDB schema."""

    @staticmethod
    def get_by_email(email):
        """Get user by email (case-insensitive)."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.find_one({
            "email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}
        })

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_by_google_id(google_id):
        """Get user by Google ID."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.find_one({"google_id": google_id})

    @staticmethod
    def get_all():
        """Get all users."""
        collection = mongo.get_collection(Collections.USERS)
        return list(collection.find())

    @staticmethod
    def create(document, user_id=None):
        """Create a new user document."""
        collection = mongo.get_collection(Collections.USERS)
        document["is_email_verified"] = False
        document["first_login_completed"] = False
        document["status"] = document.get("status", "ACTIVE")
        document["joining_date"] = document.get("joining_date")
        document["profile_image_id"] = None
        document["is_active"] = document.get("is_active", True)
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["created_by"] = user_id
        result = collection.insert_one(document)
        return str(result.inserted_id)

    @staticmethod
    def update(user_id, updates):
        """Update user document."""
        collection = mongo.get_collection(Collections.USERS)
        updates["updated_at"] = datetime.utcnow()
        collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        return UserSchema.get_by_id(user_id)

    @staticmethod
    def soft_delete(user_id):
        """Soft delete user."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"is_active": False}}
        )
