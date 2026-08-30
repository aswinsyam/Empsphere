"""
OTP Serializer.
DRF serializers for OTP.
"""
from __future__ import annotations
from rest_framework import serializers

from apps.common.core.otp import OTPPurpose


class SendOTPSerializer(serializers.Serializer):
    """Send OTP serializer."""

    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.ALL,
        default=OTPPurpose.DEFAULT,
    )

    def validate_email(self, value):
        """Normalize the email the same way the auth flows do."""
        return value.strip().lower()


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP serializer."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.ALL,
        default=OTPPurpose.DEFAULT,
    )

    def validate_email(self, value):
        """Normalize the email the same way the auth flows do."""
        return value.strip().lower()
