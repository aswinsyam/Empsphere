"""
User Serializer.
DRF serializer for user.
"""
from __future__ import annotations
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """User serialization."""

    user_id = serializers.CharField()
    employee_code = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    profile_image = serializers.CharField(required=False)
    is_email_verified = serializers.BooleanField(required=False)
    last_login = serializers.DateTimeField(required=False)