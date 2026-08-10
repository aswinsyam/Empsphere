"""
User Management Serializers.

Consolidated DRF serializers for user administration
(creating Admin/HR Manager/Employee accounts).
"""

from rest_framework import serializers

from apps.authentication.validators.email_validator import validate_email
from apps.authentication.validators.password_validator import validate_password
from apps.authentication.validators.role_validator import validate_role


class CreateUserSerializer(serializers.Serializer):
    """
    Validates a request to create a new user (Admin/HR/Employee).
    """

    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    role = serializers.CharField(required=True)
    department_id = serializers.CharField(required=False, allow_null=True)
    designation_id = serializers.CharField(required=False, allow_null=True)

    def validate_email(self, value):
        return validate_email(value)

    def validate_password(self, value):
        return validate_password(value)

    def validate_role(self, value):
        return validate_role(value)

    def validate(self, attrs):
        attrs["full_name"] = (
            f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}".strip()
        )
        return attrs
