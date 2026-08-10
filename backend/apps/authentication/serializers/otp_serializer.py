"""
OTP Serializers.

DRF serializers for one-time password flows
(email verification and password reset).
"""

from rest_framework import serializers

from apps.authentication.validators.email_validator import validate_email


class SendOTPSerializer(serializers.Serializer):
    """Validates a request to send an OTP to an email."""

    email = serializers.EmailField(required=True)
    purpose = serializers.ChoiceField(
        choices=["email_verification", "password_reset", "password_setup", "login"],
        default="email_verification",
    )

    def validate_email(self, value):
        return validate_email(value)


class VerifyOTPSerializer(serializers.Serializer):
    """Validates a request to verify an OTP."""

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    purpose = serializers.ChoiceField(
        choices=["email_verification", "password_reset", "password_setup", "login"],
        default="email_verification",
    )

    def validate_email(self, value):
        return validate_email(value)
