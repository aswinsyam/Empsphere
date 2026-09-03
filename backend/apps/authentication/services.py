"""
Authentication services.

This module contains all authentication business logic in one place:

- AuthService        — register, login, refresh token, Google login
- OTPService         — send and verify OTPs (purpose-scoped, single-use)
- PasswordService    — change / set / reset password
- UserService        — profile read / update / image upload
- Token functions    — blacklist, refresh-token check
- Reset-token funcs  — password-reset authorization tokens
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from bson import ObjectId
from django.core.mail import send_mail
from django.template.loader import render_to_string
from gridfs import GridFS, NoFile

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
    ValidationError,
)

from apps.activity_logs.services import log_activity
from apps.common.constants import (
    Collections,
    OTPPurpose,
    OTP_LENGTH,
    OTP_EXPIRY_MINUTES,
    PASSWORD_REGEX,
    PASSWORD_RULE_MESSAGE,
)
from apps.common.database import get_collection
from apps.common.settings import settings
from apps.common.utils import (
    hash_password,
    verify_password,
    generate_employee_code,
    get_user_by_email,
    get_user_by_id,
)

logger = logging.getLogger(__name__)


# =========================================================
# JWT token helpers
# =========================================================

def _generate_access_token(user):
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


def _generate_refresh_token(user):
    return jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "token_type": "refresh",
            "jti": uuid.uuid4().hex,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def _build_auth_response(user, access_token, refresh_token):
    """Standardized auth payload returned by login / register / verify."""
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


# =========================================================
# Token blacklist
# =========================================================

def blacklist_token(refresh_token):
    """Blacklist a refresh token so it can no longer be used."""
    tokens = get_collection(Collections.TOKENS)
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return False

    document = {
        "token": refresh_token,
        "user_id": payload.get("user_id"),
        "token_type": payload.get("token_type"),
        "jti": payload.get("jti") or uuid.uuid4().hex,
        "blacklisted_at": datetime.utcnow(),
    }
    exp = payload.get("exp")
    if exp:
        document["expires_at"] = datetime.utcfromtimestamp(exp)

    try:
        tokens.update_one({"token": refresh_token}, {"$set": document}, upsert=True)
        return True
    except Exception:
        return False


def is_token_blacklisted(refresh_token):
    """Check if a token is blacklisted."""
    return get_collection(Collections.TOKENS).find_one({"token": refresh_token}) is not None


def blacklist_all_user_tokens(user_id):
    """Blacklist all refresh tokens for a user."""
    get_collection(Collections.TOKENS).update_many(
        {"user_id": user_id},
        {"$set": {"blacklisted_at": datetime.utcnow()}},
    )


# =========================================================
# Password-reset token (single-use, short-lived)
# =========================================================

RESET_TOKEN_TYPE = "password_reset"


def generate_reset_token(user):
    """Issue a short-lived, single-use password reset token."""
    issued_at = datetime.utcnow()
    return jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "purpose": OTPPurpose.FORGOT_PASSWORD,
            "token_type": RESET_TOKEN_TYPE,
            "jti": uuid.uuid4().hex,
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXP_MINUTES),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_reset_token(reset_token):
    """Validate a reset token and return its payload."""
    if not reset_token:
        raise AuthenticationFailed("Password reset token is required.")
    if is_token_blacklisted(reset_token):
        raise AuthenticationFailed("This password reset token has already been used.")
    try:
        payload = jwt.decode(reset_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Password reset token has expired.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid password reset token.")

    if payload.get("token_type") != RESET_TOKEN_TYPE:
        raise AuthenticationFailed("Invalid password reset token.")
    if payload.get("purpose") != OTPPurpose.FORGOT_PASSWORD:
        raise AuthenticationFailed("Invalid password reset token.")
    if not payload.get("user_id"):
        raise AuthenticationFailed("Invalid password reset token.")
    return payload


def invalidate_reset_token(reset_token):
    """Consume a reset token so it can never be used again."""
    if not blacklist_token(reset_token):
        raise ValidationError("Could not complete the password reset.")


# =========================================================
# Google OAuth
# =========================================================

def google_verify_id_token(token: str) -> Optional[dict]:
    """Verify a Google ID token and return decoded claims."""
    try:
        return id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        return None


def google_extract_user_info(info: dict) -> dict:
    """Extract normalized user fields from Google claims."""
    return {
        "google_id": info.get("sub"),
        "email": info.get("email"),
        "first_name": info.get("given_name", ""),
        "last_name": info.get("family_name", ""),
        "full_name": info.get("name", ""),
        "profile_image_id": info.get("picture", ""),
    }


# =========================================================
# OTP Service
# =========================================================

class OTPService:
    """Send and verify one-time password codes (purpose-scoped, single-use)."""

    EMAIL_SUBJECTS = {
        OTPPurpose.FORGOT_PASSWORD: "EmpSphere Password Reset Code",
    }
    DEFAULT_EMAIL_SUBJECT = "EmpSphere OTP Code"

    def __init__(self):
        self.collection = get_collection(Collections.OTPS)

    def send_otp(self, dto):
        email = dto.get("email")
        purpose = dto.get("purpose", OTPPurpose.DEFAULT)
        self._invalidate_active(email, purpose)
        otp_code = self._generate_otp()
        self.collection.insert_one({
            "email": email,
            "purpose": purpose,
            "otp": otp_code,
            "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
            "is_used": False,
            "created_at": datetime.utcnow(),
        })
        self._send_otp_email(email, otp_code, purpose)
        return {"message": f"OTP sent to {email}", "otp_purpose": purpose}

    @staticmethod
    def _generate_otp():
        upper_bound = 10 ** OTP_LENGTH
        lower_bound = 10 ** (OTP_LENGTH - 1)
        return str(secrets.randbelow(upper_bound - lower_bound) + lower_bound)

    def _send_otp_email(self, email, otp_code, purpose):
        subject = self.EMAIL_SUBJECTS.get(purpose, self.DEFAULT_EMAIL_SUBJECT)
        context = {"otp": otp_code, "year": datetime.utcnow().year, "purpose": purpose}
        html_message = None
        try:
            html_message = render_to_string("emails/otp_email.html", context)
        except Exception:
            pass
        send_mail(
            subject=subject,
            message=f"Your OTP code is: {otp_code}",
            from_email=None,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

    def invalidate_otps(self, email, purpose):
        self._invalidate_active(email, purpose)

    def _invalidate_active(self, email, purpose):
        self.collection.update_many(
            {"email": email, "purpose": purpose, "is_used": False},
            {"$set": {"is_used": True, "used_at": datetime.utcnow()}},
        )

    def verify_otp(self, dto):
        email = dto.get("email")
        otp_code = dto.get("otp")
        purpose = dto.get("purpose", OTPPurpose.DEFAULT)
        otp_record = self.collection.find_one({
            "email": email, "purpose": purpose, "is_used": False,
        })
        if not otp_record:
            raise NotFound("OTP not found or expired.")
        if otp_record.get("otp") != otp_code:
            raise NotFound("Invalid OTP code.")
        if datetime.utcnow() > otp_record.get("expires_at"):
            raise NotFound("OTP expired.")
        if not self._mark_used(otp_record["_id"]):
            raise NotFound("OTP already used.")
        return {"message": "OTP verified successfully.", "verified": True}

    def _mark_used(self, otp_id):
        result = self.collection.update_one(
            {"_id": ObjectId(otp_id), "is_used": False},
            {"$set": {"is_used": True, "used_at": datetime.utcnow()}},
        )
        return result.modified_count == 1


# =========================================================
# User creation / update (shared helpers)
# =========================================================

def _create_user(document, user_id=None):
    """Insert a user document with default fields."""
    users = get_collection(Collections.USERS)
    document["is_email_verified"] = False
    document["first_login_completed"] = False
    document["status"] = document.get("status", "ACTIVE")
    document["joining_date"] = document.get("joining_date")
    document["profile_image_id"] = None
    document["is_active"] = document.get("is_active", True)
    document["created_at"] = datetime.utcnow()
    document["updated_at"] = datetime.utcnow()
    document["created_by"] = user_id
    result = users.insert_one(document)
    return str(result.inserted_id)


def _update_user(user_id, updates):
    """Update a user document and return the fresh record."""
    updates["updated_at"] = datetime.utcnow()
    get_collection(Collections.USERS).update_one(
        {"_id": ObjectId(user_id)}, {"$set": updates}
    )
    return get_user_by_id(user_id)


# =========================================================
# Auth Service
# =========================================================

class AuthService:
    """Authentication business logic: register, login, refresh, Google login."""

    def __init__(self):
        self.users = get_collection(Collections.USERS)
        self.otp_service = OTPService()

    def register(self, dto):
        """Register a new user (creates an ADMIN, sends email-verification OTP)."""
        email = (dto.get("email") or "").strip().lower()
        if get_user_by_email(email):
            raise ValidationError("Email already exists.")
        company_secret = dto.get("company_secret") or ""
        if company_secret != settings.COMPANY_REGISTRATION_SECRET:
            raise AuthenticationFailed("Invalid company registration code.")

        first_name = (dto.get("first_name") or "").strip()
        last_name = (dto.get("last_name") or "").strip()
        document = {
            "employee_code": generate_employee_code(),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}".strip() or None,
            "email": email,
            "phone": (dto.get("phone") or "").strip(),
            "password": hash_password(dto.get("password", "")),
            "role": "ADMIN",
            "department_id": dto.get("department_id"),
            "designation_id": dto.get("designation_id"),
        }
        user_id = _create_user(document, user_id=dto.get("created_by"))
        self.otp_service.send_otp({"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION})
        log_activity("AUTHENTICATION", "REGISTER", None, user_id, "SUCCESS",
                     f"Registered user {email}.")
        return user_id

    def login(self, dto):
        """Authenticate user and return tokens (or request OTP if email unverified)."""
        email = (dto.get("email") or "").strip().lower()
        password = dto.get("password") or ""
        user = get_user_by_email(email)
        if not user or not verify_password(password, user.get("password")):
            raise AuthenticationFailed("Invalid email or password.")
        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")
        if not user.get("is_email_verified"):
            try:
                self.otp_service.send_otp({"email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION})
            except Exception as exc:
                logger.warning("Failed to send email verification OTP for %s: %s", user.get("email"), exc)
            return {"requires_otp": True, "email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION}

        access_token = _generate_access_token(user)
        refresh_token = _generate_refresh_token(user)
        _update_user(str(user["_id"]), {"last_login": datetime.utcnow()})
        log_activity("AUTHENTICATION", "LOGIN", str(user["_id"]), str(user["_id"]), "SUCCESS",
                     f"User {user.get('email')} logged in.")
        return _build_auth_response(user, access_token, refresh_token)

    def verify_first_login(self, dto):
        """Verify email-verification OTP and issue tokens."""
        email = (dto.get("email") or "").strip().lower()
        otp_code = dto.get("otp") or ""
        purpose = dto.get("purpose") or OTPPurpose.FIRST_LOGIN
        self.otp_service.verify_otp({"email": email, "otp": otp_code, "purpose": purpose})

        user = get_user_by_email(email)
        if not user:
            raise NotFound("User not found.")
        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")

        _update_user(str(user["_id"]), {
            "is_email_verified": True,
            "first_login_completed": True,
            "last_login": datetime.utcnow(),
        })
        user = get_user_by_id(str(user["_id"]))
        access_token = _generate_access_token(user)
        refresh_token = _generate_refresh_token(user)
        log_activity("AUTHENTICATION", "EMAIL_VERIFY", str(user["_id"]), str(user["_id"]), "SUCCESS",
                     "User verified their email address.")
        return {
            "message": "Email verified successfully.",
            **_build_auth_response(user, access_token, refresh_token),
        }

    def google_login(self, dto):
        """Login or link a Google account."""
        info = google_verify_id_token(dto.get("id_token") or "")
        if not info:
            raise AuthenticationFailed("Invalid Google token.")
        google_user = google_extract_user_info(info)
        user = self.users.find_one({"google_id": google_user["google_id"]})

        if not user:
            email = google_user.get("email")
            existing_user = get_user_by_email(email) if email else None
            if existing_user:
                user = existing_user
                if not user.get("is_email_verified"):
                    try:
                        self.otp_service.send_otp({"email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION})
                    except Exception as exc:
                        logger.warning("Failed to send email verification OTP for %s: %s", user.get("email"), exc)
                    return {"requires_otp": True, "email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION}
                _update_user(str(user["_id"]), {"google_id": google_user["google_id"], "is_email_verified": True})
                user = get_user_by_id(str(user["_id"]))
            else:
                raise NotFound("No account found for this Google email. Please register first.")

        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")

        access_token = _generate_access_token(user)
        refresh_token = _generate_refresh_token(user)
        return _build_auth_response(user, access_token, refresh_token)

    def refresh_access_token(self, refresh_token):
        """Rotate refresh token: blacklist the old one and issue new tokens."""
        if is_token_blacklisted(refresh_token):
            raise AuthenticationFailed("Token has been blacklisted.")
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except Exception:
            raise AuthenticationFailed("Invalid refresh token.")

        if payload.get("token_type") != "refresh":
            raise AuthenticationFailed("Invalid token type.")

        user = get_user_by_id(payload.get("user_id"))
        if not user:
            raise AuthenticationFailed("User not found.")
        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")

        blacklist_token(refresh_token)  # rotate
        return _build_auth_response(user, _generate_access_token(user), _generate_refresh_token(user))


# =========================================================
# Password Service
# =========================================================

class PasswordService:
    """Password change, set, and reset operations."""

    FORGOT_PASSWORD_MESSAGE = "OTP sent to your email."

    def __init__(self):
        self.otp_service = OTPService()

    def change_password(self, user_id, current_password, new_password):
        """Change password after verifying the current one (current may be None for Google users)."""
        user = get_user_by_id(user_id)
        if not user:
            raise NotFound("User not found.")
        if current_password is not None:
            if not verify_password(current_password, user.get("password")):
                raise AuthenticationFailed("Current password is incorrect.")
        hashed = hash_password(new_password)
        _update_user(user_id, {"password": hashed})
        log_activity("AUTHENTICATION", "PASSWORD_CHANGE", user_id, user_id, "SUCCESS",
                     "User changed their password.")
        return {"message": "Password changed successfully."}

    def set_password(self, user_id, new_password):
        """Set a new password without verifying the current one."""
        user = get_user_by_id(user_id)
        if not user:
            raise NotFound("User not found.")
        hashed = hash_password(new_password)
        _update_user(user_id, {"password": hashed})
        log_activity("AUTHENTICATION", "PASSWORD_SET", user_id, user_id, "SUCCESS",
                     "User set their password.")
        return {"message": "Password set successfully."}

    def request_password_reset(self, email):
        """Send a forgot_password OTP (same response regardless of whether the email exists)."""
        if not email:
            raise ValidationError("Email is required.")
        user = get_user_by_email(email)
        if not user or user.get("status") == "INACTIVE":
            return {"message": self.FORGOT_PASSWORD_MESSAGE, "email_sent": False}
        self.otp_service.send_otp({"email": email, "purpose": OTPPurpose.FORGOT_PASSWORD})
        log_activity("AUTHENTICATION", "PASSWORD_RESET_REQUEST", str(user["_id"]), str(user["_id"]), "SUCCESS",
                     "Password reset OTP requested.")
        return {"message": self.FORGOT_PASSWORD_MESSAGE, "email_sent": True}

    def verify_password_reset_otp(self, email, otp):
        """Verify a forgot_password OTP and issue a single-use reset token."""
        self.otp_service.verify_otp({"email": email, "otp": otp, "purpose": OTPPurpose.FORGOT_PASSWORD})
        user = get_user_by_email(email)
        if not user:
            raise NotFound("OTP not found or expired.")
        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")
        reset_token = generate_reset_token(user)
        log_activity("AUTHENTICATION", "OTP_VERIFY", str(user["_id"]), str(user["_id"]), "SUCCESS",
                     f"OTP verified for purpose: {OTPPurpose.FORGOT_PASSWORD}.")
        return {"message": "OTP verified successfully.", "verified": True, "reset_token": reset_token}

    def reset_password(self, reset_token, new_password):
        """Reset a password using a verified reset token."""
        if not new_password:
            raise ValidationError("New password is required.")
        payload = verify_reset_token(reset_token)
        user = get_user_by_id(payload.get("user_id"))
        if not user:
            raise NotFound("User not found.")
        if payload.get("email") != user.get("email"):
            raise AuthenticationFailed("Invalid password reset token.")
        if user.get("status") == "INACTIVE":
            raise AuthenticationFailed("Your account is inactive. Please contact the administrator.")

        hashed = hash_password(new_password)
        invalidate_reset_token(reset_token)
        _update_user(str(user["_id"]), {"password": hashed})
        # Drop remaining forgot-password OTPs and invalidate existing sessions.
        self.otp_service.invalidate_otps((user.get("email") or "").strip().lower(), OTPPurpose.FORGOT_PASSWORD)
        blacklist_all_user_tokens(str(user["_id"]))
        log_activity("AUTHENTICATION", "PASSWORD_RESET", str(user["_id"]), str(user["_id"]), "SUCCESS",
                     "User reset their password via OTP.")
        return {"message": "Password reset successfully."}


# =========================================================
# User profile service
# =========================================================

class UserService:
    """User profile read and update."""

    def __init__(self):
        self.users = get_collection(Collections.USERS)

    def get_by_id(self, user_id):
        user = get_user_by_id(user_id)
        if not user:
            raise NotFound("User not found.")
        return user

    def get_by_email(self, email):
        user = get_user_by_email(email)
        if not user:
            raise NotFound("User not found.")
        return user

    def update(self, user_id, updates):
        return _update_user(user_id, updates)


# =========================================================
# Profile image service (GridFS)
# =========================================================

class ProfileImageService:
    """Store and retrieve profile images in MongoDB GridFS."""

    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    def __init__(self):
        self._fs = GridFS(get_collection(Collections.USERS).database)

    def validate_file(self, uploaded_file):
        content_type = getattr(uploaded_file, "content_type", "") or ""
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported image type: {content_type}. "
                f"Allowed: {', '.join(sorted(self.ALLOWED_CONTENT_TYPES))}."
            )
        size = getattr(uploaded_file, "size", None)
        if size is not None and size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Image size exceeds {self.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit.")

    def upload(self, user_id, uploaded_file):
        self.validate_file(uploaded_file)
        user = get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        old_file_id = user.get("profile_image_id")
        if old_file_id:
            try:
                self._fs.delete(ObjectId(old_file_id))
            except NoFile:
                pass

        file_id = self._fs.put(
            uploaded_file.read(),
            filename=uploaded_file.name,
            content_type=getattr(uploaded_file, "content_type", "application/octet-stream"),
            metadata={"user_id": user_id},
        )
        get_collection(Collections.USERS).update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_image_id": ObjectId(file_id)}},
        )
        return ObjectId(file_id)

    def get(self, file_id):
        try:
            grid_file = self._fs.get(ObjectId(file_id))
            return {
                "data": grid_file.read(),
                "filename": grid_file.filename,
                "content_type": grid_file.content_type or "application/octet-stream",
            }
        except NoFile:
            return None
