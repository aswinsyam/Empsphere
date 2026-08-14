"""
Authentication Service.
Handles authentication business logic.
"""
from __future__ import annotations

from datetime import datetime

from apps.authentication.repositories.user_repository import UserRepository
from apps.authentication.managers.otp_manager import OTPManager
from apps.authentication.managers.employee_code_manager import EmployeeCodeManager
from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
from apps.common.security.password_manager import PasswordManager
from apps.common.security.google_manager import GoogleManager
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    UnauthorizedException,
)


class AuthService(BaseService):
    """Authentication business logic."""

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.otp_manager = OTPManager()
        self.employee_code_manager = EmployeeCodeManager()
        self.token_blacklist_manager = TokenBlacklistManager()
        self.password_manager = PasswordManager()
        self.google_manager = GoogleManager()

    def register(self, dto):
        """Register a new user."""
        normalized_email = dto.email.strip().lower()
        if self.user_repository.email_exists(normalized_email):
            raise ConflictException("Email already exists.")
        employee_code = self.employee_code_manager.generate()
        hashed_password = self.password_manager.hash_password(dto.password)
        document = {
            "employee_code": employee_code,
            "first_name": dto.first_name,
            "last_name": dto.last_name,
            "full_name": dto.full_name,
            "email": normalized_email,
            "phone": dto.phone,
            "password": hashed_password,
            "role": "EMPLOYEE",
            "department_id": dto.department_id,
            "designation_id": dto.designation_id,
            "created_by": dto.created_by,
        }
        return self.user_repository.create(document, user_id=dto.created_by)

    def login(self, dto):
        """Authenticate user and return tokens."""
        user = self.user_repository.get_by_email(dto.email)
        if not user or not self.password_manager.verify_password(
            dto.password, user.get("password")
        ):
            raise UnauthorizedException("Invalid email or password.")
        if not user.get("is_email_verified"):
            self.otp_manager.create_and_send(user.get("email"), "email_verification")
            return {"requires_otp": True, "email": user.get("email")}
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        self.user_repository.update(str(user["_id"]), {"last_login": datetime.utcnow()})
        return {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def verify_email(self, token):
        """Verify email with token."""
        import jwt
        from apps.common.config.settings import settings
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except Exception:
            raise UnauthorizedException("Invalid verification token.")
        if payload.get("token_type") != "email_verification":
            raise UnauthorizedException("Invalid token type.")
        user_id = payload.get("user_id")
        if not user_id:
            raise UnauthorizedException("Invalid token payload.")
        self.user_repository.update(user_id, {"is_email_verified": True})

    def google_login(self, dto):
        """Login with Google credentials."""
        info = self.google_manager.verify_id_token(dto.id_token)
        if not info:
            raise UnauthorizedException("Invalid Google token.")
        google_user = self.google_manager.extract_user_info(info)
        user = self.user_repository.get_by_google_id(google_user["google_id"])
        if not user:
            document = {
                "employee_code": None,
                "first_name": google_user["first_name"],
                "last_name": google_user["last_name"],
                "full_name": google_user["full_name"],
                "email": google_user["email"],
                "phone": "",
                "password": None,
                "role": "EMPLOYEE",
                "department_id": None,
                "designation_id": None,
                "created_by": None,
            }
            document["login_provider"] = "GOOGLE"
            document["google_id"] = google_user["google_id"]
            document["profile_image"] = google_user["profile_image"]
            document["is_email_verified"] = True
            user_id = self.user_repository.create(document, user_id=None)
            user = self.user_repository.get_by_id(user_id)
        else:
            self.user_repository.update(
                str(user["_id"]),
                {"google_id": google_user["google_id"], "is_email_verified": True},
            )
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        return {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def refresh_token(self, refresh_token):
        """Refresh access token."""
        import jwt
        from apps.common.config.settings import settings
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except Exception:
            raise UnauthorizedException("Invalid refresh token.")
        if payload.get("token_type") != "refresh":
            raise UnauthorizedException("Invalid token type.")
        user = self.user_repository.get_by_id(payload.get("user_id"))
        if not user:
            raise UnauthorizedException("User not found.")
        # Rotate token
        self.token_blacklist_manager.blacklist(refresh_token)
        access_token = self._generate_access_token(user)
        new_refresh_token = self._generate_refresh_token(user)
        return {"access_token": access_token, "refresh_token": new_refresh_token}

    def _generate_access_token(self, user):
        """Generate access token."""
        import jwt
        from apps.common.config.settings import settings
        return jwt.encode(
            {
                "user_id": str(user["_id"]),
                "email": user.get("email"),
                "role": user.get("role"),
                "token_type": "access",
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    def _generate_refresh_token(self, user):
        """Generate refresh token."""
        import jwt
        from apps.common.config.settings import settings
        return jwt.encode(
            {
                "user_id": str(user["_id"]),
                "email": user.get("email"),
                "role": user.get("role"),
                "token_type": "refresh",
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )