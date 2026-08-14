"""
User Service.
Handles user business logic.
"""
from __future__ import annotations

from apps.authentication.repositories.user_repository import UserRepository
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import NotFoundException, ConflictException


class UserService(BaseService):
    """User business logic."""

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()

    def create(self, document, user_id):
        """Create a new user."""
        # Check if email already exists
        email = document.get("email")
        if self.user_repository.email_exists(email):
            raise ConflictException("Email already exists.")
        return self.user_repository.create(document, user_id=user_id)

    def get_by_id(self, user_id):
        """Get user by ID."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return user

    def get_all(self):
        """Get all users."""
        return self.user_repository.get_all()

    def update(self, user_id, updates):
        """Update user."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return self.user_repository.update(user_id, updates)

    def update_profile_image(self, user_id, file_url):
        """Update user profile image."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return self.user_repository.update(user_id, {"profile_image": file_url})