"""
Authentication serializers.

DRF serializers validate every request body before it reaches a service.
All auth-related serializers live in this one file.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.common.constants import OTPPurpose, PASSWORD_REGEX, PASSWORD_RULE_MESSAGE


class AuthSerializer(serializers.Serializer):
    """Used for register and login (email + password)."""

    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_secret = serializers.CharField(max_length=100, required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)


class GoogleLoginSerializer(serializers.Serializer):
    """Google login request body."""

    id_token = serializers.CharField(max_length=2000)


class SendOTPSerializer(serializers.Serializer):
    """Send OTP request body."""

    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=OTPPurpose.ALL, default=OTPPurpose.DEFAULT)

    def validate_email(self, value):
        return value.strip().lower()


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP request body."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTPPurpose.ALL, default=OTPPurpose.DEFAULT)

    def validate_email(self, value):
        return value.strip().lower()


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password request body."""

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password request body.

    The reset is authorized by the single-use ``reset_token`` handed out
    after a ``forgot_password`` OTP has been verified.
    """

    reset_token = serializers.CharField(max_length=2000, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, value):
        if not PASSWORD_REGEX.match(value or ""):
            raise serializers.ValidationError(PASSWORD_RULE_MESSAGE)
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({
                "confirm_password": "New password and confirm password do not match.",
            })
        return attrs


class UserSerializer(serializers.Serializer):
    """Serializes a user document (from MongoDB) for API responses."""

    user_id = serializers.CharField(source="_id")
    employee_code = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    department_id = serializers.CharField(required=False)
    designation_id = serializers.CharField(required=False)
    profile_image_id = serializers.CharField(required=False)
    is_email_verified = serializers.BooleanField(required=False)
    login_provider = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(required=False)
    is_active = serializers.BooleanField(required=False)
    status = serializers.CharField(required=False)
    joining_date = serializers.DateField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
