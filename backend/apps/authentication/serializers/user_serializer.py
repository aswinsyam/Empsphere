"""
User Serializer.
DRF serializer for user.
"""
from __future__ import annotations
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """User serialization."""

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