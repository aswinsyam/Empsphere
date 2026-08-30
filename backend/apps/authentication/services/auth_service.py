"""
Authentication Service.
Handles authentication business logic.
"""
from __future__ import annotations

import logging
import jwt
from datetime import datetime

from apps.authentication.repositories.user_repository import UserRepository
from apps.authentication.managers.employee_code_manager import EmployeeCodeManager
from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
from apps.authentication.services.otp_service import OTPService
from apps.common.config.settings import settings
from apps.common.core.otp import OTPPurpose
from apps.common.security.password_manager import PasswordManager
from apps.common.security.google_manager import GoogleManager
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
)

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Authentication business logic."""

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.otp_service = OTPService()
        self.employee_code_manager = EmployeeCodeManager()
        self.token_blacklist_manager = TokenBlacklistManager()
        self.password_manager = PasswordManager()
        self.google_manager = GoogleManager()

    def register(self, dto):
        """Register a new user."""
        email = (dto.get("email") or "").strip().lower()
        if self.user_repository.email_exists(email):
            raise ConflictException("Email already exists.")
        company_secret = dto.get("company_secret") or ""
        if company_secret != settings.COMPANY_REGISTRATION_SECRET:
            raise UnauthorizedException("Invalid company registration code.")
        employee_code = self.employee_code_manager.generate()
        hashed_password = self.password_manager.hash_password(dto.get("password", ""))
        first_name = (dto.get("first_name") or "").strip()
        last_name = (dto.get("last_name") or "").strip()
        document = {
            "employee_code": employee_code,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}".strip() or None,
            "email": email,
            "phone": (dto.get("phone") or "").strip(),
            "password": hashed_password,
            "role": "ADMIN",
            "department_id": dto.get("department_id"),
            "designation_id": dto.get("designation_id"),
            "created_by": dto.get("created_by"),
        }
        user_id = self.user_repository.create(document, user_id=dto.get("created_by"))
        self.otp_service.send_otp({"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION})
        return user_id

    def login(self, dto):
        """Authenticate user and return tokens."""
        email = (dto.get("email") or "").strip().lower()
        password = dto.get("password") or ""
        user = self.user_repository.get_by_email(email)
        if not user or not self.password_manager.verify_password(
            password, user.get("password")
        ):
            raise UnauthorizedException("Invalid email or password.")
        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )
        if not user.get("is_email_verified"):
            try:
                self.otp_service.send_otp({"email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION})
            except Exception as exc:
                logger.warning("Failed to send email verification OTP for %s: %s", user.get("email"), exc)
            return {"requires_otp": True, "email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION}
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        self.user_repository.update(str(user["_id"]), {"last_login": datetime.utcnow()})
        self.log_activity(
            module="AUTHENTICATION",
            action="LOGIN",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description=f"User {user.get('email')} logged in successfully.",
        )
        return self._build_auth_response(user, access_token, refresh_token)

    def verify_first_login(self, dto):
        """Verify first-login OTP and issue tokens."""
        email = (dto.get("email") or "").strip().lower()
        otp_code = dto.get("otp") or ""
        purpose = dto.get("purpose") or OTPPurpose.FIRST_LOGIN
        self.otp_service.verify_otp({"email": email, "otp": otp_code, "purpose": purpose})
        user = self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException("User not found.")
        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )
        self.user_repository.update(str(user["_id"]), {
            "is_email_verified": True,
            "first_login_completed": True,
            "last_login": datetime.utcnow(),
        })
        user = self.user_repository.get_by_id(str(user["_id"]))
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        self.log_activity(
            module="AUTHENTICATION",
            action="EMAIL_VERIFY",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description="User verified their email address.",
        )
        return {
            "message": "Email verified successfully.",
            **self._build_auth_response(user, access_token, refresh_token),
        }

    def google_login(self, dto):
        """Login with Google credentials."""
        info = self.google_manager.verify_id_token(dto.get("id_token") or "")
        if not info:
            raise UnauthorizedException("Invalid Google token.")
        google_user = self.google_manager.extract_user_info(info)
        user = self.user_repository.get_by_google_id(google_user["google_id"])
        if not user:
            existing_user = self.user_repository.get_by_email(google_user["email"]) if google_user.get("email") else None
            if existing_user:
                user = existing_user
                if not user.get("is_email_verified"):
                    try:
                        self.otp_service.send_otp({"email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION})
                    except Exception as exc:
                        logger.warning("Failed to send email verification OTP for %s: %s", user.get("email"), exc)
                    return {"requires_otp": True, "email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION}
                self.user_repository.update(
                    str(user["_id"]),
                    {"google_id": google_user["google_id"], "is_email_verified": True},
                )
                user = self.user_repository.get_by_id(str(user["_id"]))
            else:
                raise NotFoundException(
                    "No account found for this Google email. Please register first."
                )
        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        return self._build_auth_response(user, access_token, refresh_token)

    def refresh_token(self, refresh_token):
        """Refresh access token."""
        if self.token_blacklist_manager.is_blacklisted(refresh_token):
            raise UnauthorizedException("Token has been blacklisted.")
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except Exception:
            raise UnauthorizedException("Invalid refresh token.")
        if payload.get("token_type") != "refresh":
            raise UnauthorizedException("Invalid token type.")
        user = self.user_repository.get_by_id(payload.get("user_id"))
        if not user:
            raise UnauthorizedException("User not found.")
        if user.get("status") == "INACTIVE":
            raise UnauthorizedException(
                "Your account is inactive. Please contact the administrator."
            )
        # Rotate token
        self.token_blacklist_manager.blacklist(refresh_token)
        access_token = self._generate_access_token(user)
        new_refresh_token = self._generate_refresh_token(user)
        return {"access_token": access_token, "refresh_token": new_refresh_token}

    def _build_auth_response(self, user, access_token, refresh_token):
        """Build standardized authentication response payload."""
        return {
            "user_id": str(user["_id"]),
            "employee_code": user.get("employee_code"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "role": user.get("role"),
            "profile_image_id": str(user["profile_image_id"]) if user.get("profile_image_id") else None,
            "is_email_verified": user.get("is_email_verified"),
            "login_provider": user.get("login_provider"),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def _generate_access_token(self, user):
        """Generate access token."""
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