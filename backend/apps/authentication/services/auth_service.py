"""
Authentication Services.

Consolidated business logic for core authentication flows:
register, login, logout, me, refresh-token, verify-email, and google-login.
"""

import jwt
from datetime import datetime

from apps.authentication.dtos.auth_dto import (
    GoogleLoginDTO,
    LoginDTO,
    RegisterDTO,
    UpdateProfileDTO,
)
from apps.authentication.managers.employee_code_manager import EmployeeCodeManager
from apps.authentication.managers.jwt_manager import JWTManager
from apps.authentication.managers.password_manager import PasswordManager
from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
from apps.authentication.repositories.user_repository import UserRepository
from apps.authentication.schemas.user_schema import UserSchema
from apps.authentication.validators.auth_validator import AuthenticationValidator
from apps.common.base.base_service import BaseService
from apps.common.config.settings import settings
from apps.common.exceptions.custom_exception import (
    ConflictException,
    UnauthorizedException,
)
from apps.common.security.google_manager import GoogleManager
from apps.common.storage.file_manager import FileManager


# ==========================================================
# Register
# ==========================================================

class RegisterService:
    """Creates a new employee account."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.employee_code_manager = EmployeeCodeManager()
        self.password_manager = PasswordManager()

    def register(self, dto: RegisterDTO) -> str:
        """
        Register a new admin user and return the user id.

        SECURITY: The role is always forced to ADMIN by the serializer.
        The company_secret is validated by the serializer.
        """

        if self.user_repository.email_exists(dto.email):
            raise ConflictException("An account with this email already exists.")

        employee_code = self.employee_code_manager.generate()

        hashed_password = self.password_manager.hash_password(dto.password)

        document = UserSchema.create_document(
            {
                "employee_code": employee_code,
                "first_name": dto.first_name,
                "last_name": dto.last_name,
                "full_name": dto.full_name,
                "email": dto.email,
                "phone": dto.phone,
                "password": hashed_password,
                "role": "ADMIN",
                "department_id": dto.department_id,
                "designation_id": dto.designation_id,
                "created_by": dto.created_by,
            }
        )

        return self.user_repository.create(document, user_id=dto.created_by)


# ==========================================================
# Login
# ==========================================================

class LoginService(BaseService):
    """Authenticates a user and returns tokens."""

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
        self.validator = AuthenticationValidator()

    def login(self, dto: LoginDTO) -> dict:
        """Validate credentials and issue access + refresh tokens."""

        user = self.user_repository.get_by_email(dto.email)

        if not user or not self.password_manager.verify_password(
            dto.password, user.get("password")
        ):
            raise UnauthorizedException("Invalid email or password.")

        self.validator.validate_login(user)

        access_token = self.jwt_manager.generate_access_token(user)
        refresh_token = self.jwt_manager.generate_refresh_token(user)

        self.user_repository.update(
            str(user["_id"]),
            {"last_login": datetime.utcnow()},
        )

        self.log_activity(
            module="AUTHENTICATION",
            action="LOGIN",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description="User logged in",
        )

        return {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


# ==========================================================
# Logout
# ==========================================================

class LogoutService:
    """Blacklists the refresh token on logout."""

    def __init__(self):
        self.token_blacklist_manager = TokenBlacklistManager()

    def logout(self, refresh_token: str) -> None:
        """Blacklist the given refresh token."""
        self.token_blacklist_manager.blacklist(refresh_token)


# ==========================================================
# Me
# ==========================================================

class MeService:
    """Returns current user details."""

    def __init__(self):
        self.user_repository = UserRepository()

    @staticmethod
    def sanitize_profile(user: dict) -> dict:
        """
        Build a safe profile dict that never exposes sensitive internal
        fields such as password hashes, reset/refresh tokens, or google_id.
        """
        return {
            "user_id": str(user["_id"]),
            "employee_code": user.get("employee_code"),
            "full_name": user.get("full_name"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "role": user.get("role"),
            "department_id": user.get("department_id"),
            "designation_id": user.get("designation_id"),
            "profile_image": user.get("profile_image"),
            "is_email_verified": user.get("is_email_verified"),
            "last_login": user.get("last_login"),
        }

    def get_profile(self, user_id: str) -> dict:
        """Fetch and return a sanitized user profile."""

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise UnauthorizedException("User not found.")

        return self.sanitize_profile(user)


# ==========================================================
# Profile Update
# ==========================================================

class UpdateProfileService:
    """
    Updates the current user's editable profile fields.

    Only the owner of the account may update their own profile. The role
    and email are intentionally immutable through this endpoint.
    """

    def __init__(self):
        self.user_repository = UserRepository()

    def update_profile(self, dto: UpdateProfileDTO) -> dict:
        """Apply editable profile changes and return the sanitized profile."""

        user = self.user_repository.get_by_id(dto.user_id)

        if not user:
            raise UnauthorizedException("User not found.")

        updates: dict = {}

        if dto.first_name is not None:
            updates["first_name"] = dto.first_name
        if dto.last_name is not None:
            updates["last_name"] = dto.last_name
        if dto.phone is not None:
            updates["phone"] = dto.phone

        if "first_name" in updates or "last_name" in updates:
            first = updates.get("first_name", user.get("first_name")) or ""
            last = updates.get("last_name", user.get("last_name")) or ""
            updates["full_name"] = f"{first} {last}".strip()

        if updates:
            self.user_repository.update(dto.user_id, updates, user_id=dto.user_id)

        updated_user = self.user_repository.get_by_id(dto.user_id)
        return MeService.sanitize_profile(updated_user)


# ==========================================================
# Profile Image Upload
# ==========================================================

class UploadProfileImageService:
    """
    Uploads and stores the current user's profile image.

    The image is stored via the existing FileManager and only the file path
    is persisted on the user document (never the raw binary).
    """

    def __init__(self):
        self.user_repository = UserRepository()
        self.file_manager = FileManager()

    def upload(self, user_id: str, uploaded_file) -> dict:
        """Store the image and return the sanitized profile."""

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found.")

        directory = "profiles"
        profile_image = self.file_manager.save(uploaded_file, directory)

        self.user_repository.update(
            user_id,
            {"profile_image": profile_image},
            user_id=user_id,
        )

        updated_user = self.user_repository.get_by_id(user_id)
        return MeService.sanitize_profile(updated_user)


# ==========================================================
# Refresh Token
# ==========================================================

class RefreshTokenService:
    """Exchanges a refresh token for a fresh access token."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.jwt_manager = JWTManager()
        self.token_blacklist_manager = TokenBlacklistManager()

    def refresh(self, refresh_token: str) -> dict:
        """
        Return a new access token for a valid refresh token.

        Implements refresh-token rotation: the presented refresh token is
        revoked (blacklisted) and a brand-new refresh token is issued. A
        rotated/revoked refresh token can no longer be reused.
        """

        if self.token_blacklist_manager.is_blacklisted(refresh_token):
            raise UnauthorizedException("Refresh token has been revoked.")

        try:
            payload = self.jwt_manager.decode_token(refresh_token)
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid or expired refresh token.")

        if payload.get("token_type") != "refresh":
            raise UnauthorizedException("Invalid token type.")

        user = self.user_repository.get_by_id(payload.get("user_id"))

        if not user:
            raise UnauthorizedException("User not found.")

        # Rotate: revoke the presented refresh token before issuing a new one.
        self.token_blacklist_manager.blacklist(refresh_token)

        return {
            "access_token": self.jwt_manager.generate_access_token(user),
            "refresh_token": self.jwt_manager.generate_refresh_token(user),
        }


# ==========================================================
# Verify Email
# ==========================================================

class VerifyEmailService:
    """Verifies a user's email address."""

    def __init__(self):
        self.user_repository = UserRepository()

    def verify_email(self, token: str) -> None:
        """Validate the verification token and mark email as verified."""

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError:
            raise UnauthorizedException("The verification token is invalid or has expired.")

        if payload.get("token_type") != "email_verification":
            raise UnauthorizedException("Invalid token type.")

        user_id = payload.get("user_id")

        if not user_id:
            raise UnauthorizedException("Invalid token payload.")

        self.user_repository.update(
            user_id,
            {"is_email_verified": True},
            user_id=user_id,
        )


# ==========================================================
# Google Login
# ==========================================================

class GoogleLoginService:
    """Logs in or creates a user from Google credentials."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.jwt_manager = JWTManager()
        self.google_manager = GoogleManager()

    def google_login(self, dto: GoogleLoginDTO) -> dict:
        """Verify the Google token and return app tokens."""

        info = self.google_manager.verify_id_token(dto.id_token)

        if not info:
            raise UnauthorizedException("Invalid Google token.")

        google_user = self.google_manager.extract_user_info(info)

        user = self.user_repository.get_by_google_id(google_user["google_id"])

        if not user:
            user = self.user_repository.get_by_email(google_user["email"])

        if not user:
            document = UserSchema.create_document(
                {
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
            )
            document["login_provider"] = "GOOGLE"
            document["google_id"] = google_user["google_id"]
            document["profile_image"] = google_user["profile_image"]
            document["is_email_verified"] = True

            user_id = self.user_repository.create(document)
            user = self.user_repository.get_by_id(user_id)
        else:
            self.user_repository.update(
                str(user["_id"]),
                {"google_id": google_user["google_id"], "is_email_verified": True},
            )

        return {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "access_token": self.jwt_manager.generate_access_token(user),
            "refresh_token": self.jwt_manager.generate_refresh_token(user),
        }
