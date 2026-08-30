"""
OTP View.
Handles HTTP API requests for OTP send and verification.
"""
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from apps.authentication.services.otp_service import OTPService
from apps.authentication.services.auth_service import AuthService
from apps.authentication.services.password_service import PasswordService
from apps.authentication.serializers.otp_serializer import SendOTPSerializer, VerifyOTPSerializer
from apps.common.base.base_controller import BaseController
from apps.common.core.otp import OTPPurpose


class OTPView(APIView, BaseController):
    """Handle OTP send and verification requests."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Handle OTP send or verify requests based on the matched URL name."""
        url_name = request.resolver_match.url_name if request.resolver_match else None

        if url_name == "send-otp":
            serializer = SendOTPSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.validated_data.get("purpose") == OTPPurpose.FORGOT_PASSWORD:
                    # Password reset OTPs are only issued through
                    # /forgot-password/ so unknown accounts are never
                    # revealed and no email is sent to them.
                    result = PasswordService().request_password_reset(
                        serializer.validated_data["email"]
                    )
                    return self.success(
                        message=result["message"],
                        data=None,
                        status_code=status.HTTP_200_OK,
                    )
                service = OTPService()
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

        if url_name == "verify-otp":
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid():
                purpose = serializer.validated_data.get("purpose", OTPPurpose.DEFAULT)
                user_id = None

                if purpose == OTPPurpose.FORGOT_PASSWORD:
                    # Password reset: verify the OTP and hand out a
                    # single-use reset token. The user is NOT logged in
                    # and no access/refresh token is issued here.
                    result = PasswordService().verify_password_reset_otp(
                        email=serializer.validated_data["email"],
                        otp=serializer.validated_data["otp"],
                    )
                    return self.success(
                        message=result["message"],
                        data=result,
                        status_code=status.HTTP_200_OK,
                    )

                if purpose == OTPPurpose.FIRST_LOGIN:
                    result = AuthService().verify_first_login(serializer.validated_data)
                    user_id = result.get("user_id")
                else:
                    service = OTPService()
                    result = service.verify_otp(serializer.validated_data)
                    if purpose == OTPPurpose.EMAIL_VERIFICATION:
                        email = serializer.validated_data.get("email")
                        if email:
                            from apps.authentication.repositories.user_repository import UserRepository
                            user = UserRepository().get_by_email(email)
                            if user:
                                user_id = str(user["_id"])
                                UserRepository().update(str(user["_id"]), {"is_email_verified": True})
                                user = UserRepository().get_by_id(str(user["_id"]))
                                auth_service = AuthService()
                                access_token = auth_service._generate_access_token(user)
                                refresh_token = auth_service._generate_refresh_token(user)
                                result = {
                                    "message": result["message"],
                                    "verified": True,
                                    **auth_service._build_auth_response(user, access_token, refresh_token),
                                }
                if user_id:
                    from apps.common.base.base_service import BaseService
                    BaseService().log_activity(
                        module="AUTHENTICATION",
                        action="OTP_VERIFY",
                        performed_by=user_id,
                        target_id=user_id,
                        status="SUCCESS",
                        description=f"OTP verified for purpose: {purpose}.",
                    )
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

        return self.error(
            message="Unknown OTP action.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
