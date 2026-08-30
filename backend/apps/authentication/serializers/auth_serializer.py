"""
Authentication Serializer.
DRF serializers for authentication.
"""
from __future__ import annotations
from rest_framework import serializers


class AuthSerializer(serializers.Serializer):
    """Authentication request/response serializer."""

    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_secret = serializers.CharField(max_length=100, required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)


class GoogleLoginSerializer(serializers.Serializer):
    """Google login serializer."""

    id_token = serializers.CharField(max_length=2000)