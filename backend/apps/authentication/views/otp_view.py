"""
OTP View.
Handles HTTP API requests for OTP send and verification.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.services.otp_service import OTPService
from apps.authentication.serializers.otp_serializer import SendOTPSerializer, VerifyOTPSerializer
from apps.common.base.base_controller import BaseController


class OTPView(APIView, BaseController):
    """Handle OTP send and verification requests."""

    def post(self, request):
        purpose = request.data.get("purpose", "email_verification")
        if purpose == "verify":
            serializer = VerifyOTPSerializer(data=request.data)
        else:
            serializer = SendOTPSerializer(data=request.data)

        if serializer.is_valid():
            service = OTPService()
            if purpose == "verify":
                result = service.verify_otp(serializer.validated_data)
            else:
                result = service.send_otp(serializer.validated_data)
            return self.success(
                message=result["message"],
                data=result,
                status_code=status.HTTP_200_OK,
            )
        return self.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
