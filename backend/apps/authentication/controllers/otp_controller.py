"""
OTP Controllers.

Consolidated API endpoints for one-time password flows:
send-otp and verify-otp.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.authentication.dtos.otp_dto import SendOTPDTO, VerifyOTPDTO
from apps.authentication.serializers.otp_serializer import (
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from apps.authentication.services.otp_service import OTPService
from apps.common.base.base_controller import BaseController


class SendOTPController(APIView, BaseController):
    """Endpoint to send an OTP to a user's email."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.otp_service = OTPService()

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)

        # SECURITY: For password_setup, the email must come from the
        # authenticated user's session — never from the request body.
        # This prevents a user from requesting a password-setup OTP for
        # an arbitrary email address.
        if data.get("purpose") == "password_setup":
            user = getattr(request, "user", None)
            if not user or not user.get("_id"):
                raise PermissionError("Authentication required.")
            data["email"] = user.get("email")

        dto = SendOTPDTO(**data)

        self.otp_service.send_otp(dto)

        return self.success(
            message="OTP sent to your email.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


class VerifyOTPController(APIView, BaseController):
    """Endpoint to verify an OTP."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.otp_service = OTPService()

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)

        # SECURITY: For password_setup, the email must come from the
        # authenticated user's session — never from the request body.
        if data.get("purpose") == "password_setup":
            user = getattr(request, "user", None)
            if not user or not user.get("_id"):
                raise PermissionError("Authentication required.")
            data["email"] = user.get("email")

        dto = VerifyOTPDTO(**data)

        self.otp_service.verify_otp(dto)

        return self.success(
            message="OTP verified successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )
