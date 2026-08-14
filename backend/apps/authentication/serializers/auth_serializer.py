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
    confirm_password = serializers.CharField(max_length=128, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    company_secret = serializers.CharField(max_length=100, required=False)


class GoogleLoginSerializer(serializers.Serializer):
    """Google login serializer."""

    id_token = serializers.CharField(max_length=2000)