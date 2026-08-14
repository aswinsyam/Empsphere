"""
User Repository.
Handles user database operations.
"""
from __future__ import annotations

from apps.authentication.schemas.user_schema import UserSchema


class UserRepository:
    """User data access layer."""

    def email_exists(self, email):
        """Check if email already exists."""
        return UserSchema.get_by_email(email) is not None

    def get_by_email(self, email):
        """Get user by email."""
        return UserSchema.get_by_email(email)

    def get_by_id(self, user_id):
        """Get user by ID."""
        return UserSchema.get_by_id(user_id)

    def get_by_google_id(self, google_id):
        """Get user by Google ID."""
        return UserSchema.get_by_google_id(google_id)

    def get_all(self):
        """Get all users."""
        return UserSchema.get_all()

    def create(self, document, user_id):
        """Create a new user document."""
        return UserSchema.create(document, user_id=user_id)

    def update(self, user_id, updates):
        """Update user document."""
        return UserSchema.update(user_id, updates)

    def soft_delete(self, user_id):
        """Soft delete user."""
        return UserSchema.soft_delete(user_id)