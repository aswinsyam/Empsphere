"""
Password Management Serializers.

Consolidated DRF serializers for all password flows:
change-password, forgot-password, and reset-password.
"""

from rest_framework import serializers

from apps.authentication.validators.email_validator import validate_email
from apps.authentication.validators.password_validator import validate_password


class ChangePasswordSerializer(serializers.Serializer):
    """Validates an authenticated password change request."""

    old_password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate_new_password(self, value):
        return validate_password(value)


class ForgotPasswordSerializer(serializers.Serializer):
    """Validates a forgot password request."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return validate_email(value)


class ResetPasswordSerializer(serializers.Serializer):
    """Validates a reset password request."""

    token = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate_new_password(self, value):
        return validate_password(value)


class SetPasswordSerializer(serializers.Serializer):
    """Validates a Google-authenticated user setting a local password."""

    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate_new_password(self, value):
        return validate_password(value)
