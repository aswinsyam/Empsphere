"""
Department Serializer.

Validates department request payloads.
"""

from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    """Validates department create/update requests."""

    name = serializers.CharField(required=True, max_length=120)
    code = serializers.CharField(required=True, max_length=20)
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)
    head_user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    organization_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        attrs["name"] = attrs.get("name", "").strip()
        attrs["code"] = attrs.get("code", "").strip().upper()
        if not attrs.get("description"):
            attrs["description"] = None
        if not attrs.get("head_user_id"):
            attrs["head_user_id"] = None
        if not attrs.get("organization_id"):
            attrs["organization_id"] = None
        return attrs
