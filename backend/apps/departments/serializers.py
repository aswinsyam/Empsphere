"""
Department serializers.
DRF serializers for department create / update validation.
"""
from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    """Department serialization and validation for create."""

    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    head_user_id = serializers.CharField(max_length=255, required=False)
    organization_id = serializers.CharField(max_length=255, required=False)


class DepartmentUpdateSerializer(serializers.Serializer):
    """Department update serializer — only mutable fields."""

    name = serializers.CharField(max_length=255, required=False)
    code = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=500, required=False)
    head_user_id = serializers.CharField(max_length=255, required=False)
    organization_id = serializers.CharField(max_length=255, required=False)
    is_active = serializers.BooleanField(required=False)
