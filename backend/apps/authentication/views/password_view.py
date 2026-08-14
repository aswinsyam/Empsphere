"""
Password View.
Handles HTTP API requests for password operations.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.services.password_service import PasswordService
from apps.authentication.services.otp_service import OTPService
from apps.common.responses.api_response import ApiResponse


class PasswordView(APIView):
    """Handle password-related API requests."""

    def post(self, request):
        path = request.path.rstrip("/")
        action = path.rsplit("/", 1)[-1]

        if action == "change-password":
            return self._change_password(request)
        elif action == "forgot-password":
            return self._forgot_password(request)
        elif action == "reset-password":
            return self._reset_password(request)
        elif action == "set-password":
            return self._set_password(request)
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

    def _forgot_password(self, request):
        """Send password reset OTP."""
        email = request.data.get("email")
        if not email:
            return ApiResponse.error(
                message="Email is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        otp_service = OTPService()
        otp_service.send_otp({"email": email, "purpose": "password_reset"})
        return ApiResponse.success(
            message="If an account exists for that email, a reset OTP has been sent.",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    def _reset_password(self, request):
        """Reset password using OTP token."""
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return ApiResponse.error(
                message="token and new_password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        otp_service = OTPService()
        verification = otp_service.verify_otp({
            "email": request.data.get("email", ""),
            "otp": token,
            "purpose": "password_reset",
        })
        # After OTP verification, update the user's password.
        # The frontend should also send the email so we know which user to update.
        email = request.data.get("email")
        if not email:
            return ApiResponse.error(
                message="Email is required for password reset.",
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
            message="Password reset successfully.",
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
            "purpose": "password_setup",
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