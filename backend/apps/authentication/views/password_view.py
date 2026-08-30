"""
Password View.
Handles HTTP API requests for password operations.
"""
from __future__ import annotations

from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from apps.authentication.serializers.password_serializer import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from apps.authentication.services.password_service import PasswordService
from apps.authentication.services.otp_service import OTPService
from apps.common.core.otp import OTPPurpose
from apps.common.responses.api_response import ApiResponse


class PasswordView(APIView):
    """Handle password-related API requests."""

    def get_permissions(self):
        if self.request.method == "POST":
            path = self.request.path.rstrip("/")
            action = path.rsplit("/", 1)[-1]
            if action in ("change-password", "forgot-password", "reset-password"):
                return [AllowAny()]
        return [AllowAny()]

    def post(self, request):
        """Dispatch password change, set-password, forgot-password, or reset-password requests."""
        path = request.path.rstrip("/")
        action = path.rsplit("/", 1)[-1]

        if action == "change-password":
            return self._change_password(request)
        elif action == "set-password":
            return self._set_password(request)
        elif action == "forgot-password":
            return self._forgot_password(request)
        elif action == "reset-password":
            return self._reset_password(request)
        else:
            return ApiResponse.error(
                message="Unknown password action.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def _change_password(self, request):
        """Change password for authenticated user."""
        current_password = request.data.get("current_password") or request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not current_password or not new_password:
            return ApiResponse.error(
                message="current_password and new_password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        service = PasswordService()
        result = service.change_password(
            user_id=str(request.user["_id"]),
            current_password=current_password,
            new_password=new_password,
        )
        return ApiResponse.success(
            message=result["message"],
            data=result,
            status_code=status.HTTP_200_OK,
        )

    def _set_password(self, request):
        """Set password for Google users using OTP."""
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        if not otp or not new_password:
            return ApiResponse.error(
                message="otp and new_password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        otp_service = OTPService()
        verification = otp_service.verify_otp({
            "email": request.data.get("email", ""),
            "otp": otp,
            "purpose": OTPPurpose.PASSWORD_SETUP,
        })
        email = request.data.get("email")
        if not email:
            return ApiResponse.error(
                message="Email is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        from apps.authentication.repositories.user_repository import UserRepository
        user = UserRepository().get_by_email(email)
        if not user:
            return ApiResponse.error(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        password_service = PasswordService()
        result = password_service.change_password(
            user_id=str(user["_id"]),
            current_password=None,
            new_password=new_password,
        )
        return ApiResponse.success(
            message="Password set successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    def _forgot_password(self, request):
        """Send a password reset OTP to the user's registered email."""
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        service = PasswordService()
        result = service.request_password_reset(serializer.validated_data["email"])

        # The same response is returned whether or not the account exists.
        return ApiResponse.success(
            message=result["message"],
            status_code=status.HTTP_200_OK,
        )

    def _reset_password(self, request):
        """Reset the password using the single-use reset token."""
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        # Accept `new_password` as an alias for `password`.
        if not data.get("password") and data.get("new_password"):
            data["password"] = data.get("new_password")

        serializer = ResetPasswordSerializer(data=data)
        if not serializer.is_valid():
            return ApiResponse.error(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        service = PasswordService()
        result = service.reset_password(
            reset_token=serializer.validated_data["reset_token"],
            new_password=serializer.validated_data["password"],
        )

        return ApiResponse.success(
            message=result["message"],
            data=None,
            status_code=status.HTTP_200_OK,
        )