from __future__ import annotations

from rest_framework import serializers
from django.core.validators import RegexValidator


class EmployeeSerializer(serializers.Serializer):
    """Employee serialization and validation for create/update."""

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=128, required=False, allow_blank=True)
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r"^[+]?[\d\s\-()]{7,15}$",
                message="Enter a valid phone number (digits, spaces, hyphens, parentheses, and leading + allowed).",
            )
        ],
    )
    role = serializers.CharField(required=False, allow_blank=True)
    department_id = serializers.CharField(required=False, allow_blank=True)
    designation_id = serializers.CharField(required=False, allow_blank=True)
    joining_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)
    employee_code = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        is_create = kwargs.pop("is_create", False)
        super().__init__(*args, **kwargs)
        if is_create:
            self.fields["first_name"].required = True
            self.fields["last_name"].required = True
            self.fields["email"].required = True
            self.fields["role"].required = True
            self.fields["password"].required = True
            self.fields["password"].allow_blank = False
