"""
Authentication Serializers.

Consolidated DRF serializers for core authentication flows:
register, login, refresh-token, and google-login.
"""

from rest_framework import serializers

from apps.authentication.validators.email_validator import validate_email
from apps.authentication.validators.password_validator import validate_password
from apps.common.exceptions.custom_exception import ValidationException as AppValidationException


# ==========================================================
# Register
# ==========================================================

class RegisterSerializer(serializers.Serializer):
    """
    Validates a public admin registration request.

    SECURITY: Public registration must NEVER allow a caller to choose a
    privileged role. The role is always forced to ``ADMIN``. The
    ``company_secret`` must match the backend configuration. Privileged
    roles may only be assigned via the authorized ``create-user`` endpoint.
    """

    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)
    company_secret = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        return validate_email(value)

    def validate_password(self, value):
        try:
            return validate_password(value)
        except AppValidationException as e:
            raise serializers.ValidationError(str(e))

    def validate(self, attrs):
        # Validate company secret
        from apps.common.config.settings import settings
        if attrs.get("company_secret") != settings.COMPANY_REGISTRATION_SECRET:
            raise serializers.ValidationError(
                {"company_secret": "Invalid company registration secret."}
            )

        # Validate password confirmation
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )

        # Always force public registrations to ADMIN regardless of any
        # role the caller may have submitted.
        attrs["role"] = "ADMIN"
        attrs["full_name"] = f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}".strip()

        # Remove confirm_password and company_secret before passing to DTO
        attrs.pop("confirm_password", None)
        attrs.pop("company_secret", None)

        return attrs


# ==========================================================
# Login
# ==========================================================

class LoginSerializer(serializers.Serializer):
    """Validates login request."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate_email(self, value):
        return value.lower()


# ==========================================================
# Refresh Token
# ==========================================================

class RefreshTokenSerializer(serializers.Serializer):
    """Validates refresh token request."""

    refresh_token = serializers.CharField(required=True, write_only=True)


# ==========================================================
# Google Login
# ==========================================================

class GoogleLoginSerializer(serializers.Serializer):
    """Validates Google login request."""

    id_token = serializers.CharField(required=True, write_only=True)


# ==========================================================
# Profile Update
# ==========================================================

class UpdateProfileSerializer(serializers.Serializer):
    """Validates an authenticated user's profile update request."""

    first_name = serializers.CharField(
        required=False, allow_blank=False, max_length=100
    )
    last_name = serializers.CharField(
        required=False, allow_blank=False, max_length=100
    )
    phone = serializers.CharField(
        required=False, allow_blank=True, max_length=20
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "At least one profile field must be provided."
            )
        return attrs
