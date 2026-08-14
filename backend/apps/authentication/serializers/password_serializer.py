"""
Password Serializer.
DRF serializer for password.
"""
from __future__ import annotations
from rest_framework import serializers


class PasswordSerializer(serializers.Serializer):
    """Password change serializer."""

    user_id = serializers.CharField()
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)