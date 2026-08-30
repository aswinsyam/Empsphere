"""
Password Serializer.
DRF serializers for the password reset flow.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.common.core.regex import PASSWORD_REGEX, PASSWORD_RULE_MESSAGE


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password request serializer."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Normalize the email the same way the auth flows do."""
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer.

    The reset is authorized by the single-use ``reset_token`` handed out
    after a ``forgot_password`` OTP has been verified. The OTP itself is
    never accepted here.
    """

    reset_token = serializers.CharField(max_length=2000, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, value):
        """Enforce the project-wide password policy."""
        if not PASSWORD_REGEX.match(value or ""):
            raise serializers.ValidationError(PASSWORD_RULE_MESSAGE)
        return value

    def validate(self, attrs):
        """Ensure the new password and its confirmation match."""
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({
                "confirm_password": "New password and confirm password do not match.",
            })
        return attrs
