"""
Authentication business validator.
"""

from apps.authentication.repositories.user_repository import UserRepository
from apps.common.exceptions.custom_exception import CustomException


class AuthenticationValidator:
    """
    Business validation for authentication.
    """

    def __init__(self):
        self.user_repository = UserRepository()

    def validate_registration(self, dto) -> None:
        """
        Validate registration business rules.
        """

        if self.user_repository.email_exists(dto.email):
            raise CustomException(
                message="Email already exists."
            )

        # Phone validation will be added later.
        # Role permission validation will be added later.
        # First Super Admin validation will be added later.



    def validate_login(self, user) -> None:
        """
        Business validation for login.
        """

        if not user:
            raise CustomException(
                message="Invalid email or password."
            )

        if user.get("is_deleted"):
            raise CustomException(
                message="Account has been deleted."
            )

        if not user.get("is_active"):
            raise CustomException(
                message="Account is deactivated."
            )