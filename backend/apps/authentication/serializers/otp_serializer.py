"""
OTP Serializer.
DRF serializers for OTP.
"""
from __future__ import annotations
from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    """Send OTP serializer."""

    email = serializers.EmailField()
    purpose = serializers.CharField(max_length=50, default="email_verification")


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP serializer."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField(max_length=50, default="email_verification")