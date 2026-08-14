"""
User Schema.
MongoDB schema definitions for user.
"""
from __future__ import annotations
import jwt
from datetime import datetime
from apps.common.config.settings import settings
from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class UserSchema:
    """User MongoDB schema."""

    @staticmethod
    def get_by_email(email):
        """Get user by email."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.find_one({"email": email})

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.find_one({"_id": user_id})

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
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        result = collection.insert_one(document)
        return result.inserted_id

    @staticmethod
    def update(user_id, updates):
        """Update user document."""
        collection = mongo.get_collection(Collections.USERS)
        updates["updated_at"] = datetime.utcnow()
        return collection.update_one({"_id": user_id}, {"$set": updates})

    @staticmethod
    def soft_delete(user_id):
        """Soft delete user."""
        collection = mongo.get_collection(Collections.USERS)
        return collection.update_one(
            {"_id": user_id}, {"$set": {"is_active": False}}
        )
