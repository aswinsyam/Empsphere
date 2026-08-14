"""
Department Serializer.
DRF serializer for department.
"""
from __future__ import annotations
from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    """Department serialization."""

    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=500, required=False)
    head_user_id = serializers.CharField(max_length=255, required=False)
    organization_id = serializers.CharField(max_length=255, required=False)