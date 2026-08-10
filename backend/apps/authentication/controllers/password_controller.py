"""
Password Management Controllers.

Consolidated API endpoints for all password flows:
change-password, forgot-password, and reset-password.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.authentication.dtos.password_dto import (
    ChangePasswordDTO,
    ForgotPasswordDTO,
    ResetPasswordDTO,
    SetPasswordDTO,
)
from apps.authentication.serializers.password_serializer import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    SetPasswordSerializer,
)
from apps.authentication.services.password_service import (
    ChangePasswordService,
    ForgotPasswordService,
    ResetPasswordService,
    SetPasswordService,
)
from apps.common.base.base_controller import BaseController


class ChangePasswordController(APIView, BaseController):
    """Endpoint for an authenticated password change."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.change_password_service = ChangePasswordService()

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = ChangePasswordDTO(
            **serializer.validated_data,
            user_id=str(request.user["_id"]),
        )

        self.change_password_service.change_password(dto)

        return self.success(
            message="Password changed successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


class ForgotPasswordController(APIView, BaseController):
    """Endpoint to request a password reset email."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forgot_password_service = ForgotPasswordService()

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = ForgotPasswordDTO(**serializer.validated_data)

        self.forgot_password_service.forgot_password(dto)

        return self.success(
            message="If an account exists, a reset link has been sent.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


class ResetPasswordController(APIView, BaseController):
    """Endpoint to set a new password using a reset token."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_password_service = ResetPasswordService()

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = ResetPasswordDTO(**serializer.validated_data)

        self.reset_password_service.reset_password(dto)

        return self.success(
            message="Password reset successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


class SetPasswordController(APIView, BaseController):
    """Endpoint for a Google user to set a local password."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password_service = SetPasswordService()

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = SetPasswordDTO(
            **serializer.validated_data,
            user_id=str(request.user["_id"]),
        )

        self.set_password_service.set_password(dto)

        return self.success(
            message="Password set successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )
