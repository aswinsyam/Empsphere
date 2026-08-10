"""
User Repository.

Contains user-specific database operations.
"""

from apps.common.base.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository for the users collection.
    """

    COLLECTION_NAME = "users"

    def __init__(self):
        super().__init__(self.COLLECTION_NAME)

    def get_by_email(self, email: str):
        """
        Get a user by email.
        """
        return self.get_one({"email": email.lower()})

    def get_by_employee_code(self, employee_code: str):
        """
        Get a user by employee code.
        """
        return self.get_one({"employee_code": employee_code})

    def get_by_google_id(self, google_id: str):
        """
        Get a user by Google ID.
        """
        return self.get_one({"google_id": google_id})

    def email_exists(self, email: str) -> bool:
        """
        Check whether an email already exists.
        """
        return self.exists({"email": email.lower()})

    def employee_code_exists(self, employee_code: str) -> bool:
        """
        Check whether an employee code already exists.
        """
        return self.exists({"employee_code": employee_code})
    