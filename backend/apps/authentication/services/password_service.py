"""
Password Service.
Handles password operations.
"""
from __future__ import annotations

from apps.authentication.repositories.user_repository import UserRepository
from apps.common.base.base_service import BaseService
from apps.common.security.password_manager import PasswordManager
from apps.common.exceptions.custom_exception import NotFoundException, UnauthorizedException


class PasswordService(BaseService):
    """Password business logic."""

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()

    def hash_password(self, password):
        """Hash a password."""
        return self.password_manager.hash_password(password)

    def verify_password(self, plain_password, hashed_password):
        """Verify password."""
        return self.password_manager.verify_password(plain_password, hashed_password)

    def change_password(self, user_id, current_password, new_password):
        """Change user password after verifying current password."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        if not self.password_manager.verify_password(
            current_password, user.get("password")
        ):
            raise UnauthorizedException("Current password is incorrect.")
        hashed = self.password_manager.hash_password(new_password)
        return self.user_repository.update(user_id, {"password": hashed})

    def set_password(self, user_id, new_password):
        """Set a new password without verifying the current one."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        hashed = self.password_manager.hash_password(new_password)
        return self.user_repository.update(user_id, {"password": hashed})