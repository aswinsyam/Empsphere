"""
Authentication views.

Single file merging what used to live in seven separate modules
under ``authentication/views/``.
"""
from __future__ import annotations

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from bson import ObjectId
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.common.permissions import IsAuthenticatedUser
from rest_framework.views import APIView

from apps.activity_logs.services import log_activity
from apps.authentication.services import (
    AuthService,
    OTPService,
    PasswordService,
    ProfileImageService,
    UserService,
    blacklist_token,
)
from apps.authentication.serializers import (
    AuthSerializer,
    ForgotPasswordSerializer,
    GoogleLoginSerializer,
    ResetPasswordSerializer,
    SendOTPSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from apps.common.constants import Collections, OTPPurpose
from apps.common.database import get_collection
from apps.common.responses import error, success


class RegisterView(APIView):
    """Register a new user."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        result = AuthService().register(serializer.validated_data)
        return success(
            "User registered successfully.",
            data={"user_id": str(result)},
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user and return tokens."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        result = AuthService().login(serializer.validated_data)
        return success("Login successful.", data=result)


class LogoutView(APIView):
    """Blacklist the refresh token and end the session."""

    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            blacklist_token(refresh_token)
        user_id = str(request.user["_id"]) if isinstance(request.user, dict) else None
        if user_id:
            log_activity(
                "AUTHENTICATION", "LOGOUT",
                user_id, user_id,
                "SUCCESS", "User logged out successfully.",
            )
        return success("Logged out successfully.")


class RefreshTokenView(APIView):
    """Exchange a refresh token for a new access token."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return error("Refresh token is required.", status_code=status.HTTP_400_BAD_REQUEST)
        result = AuthService().refresh_access_token(refresh_token)
        return success("Token refreshed successfully.", data=result)


class UserView(APIView):
    """Handle user profile retrieve and update."""

    def get(self, request):
        user = UserService().get_by_id(str(request.user["_id"]))
        return success("Profile retrieved successfully.", data=UserSerializer(user).data)

    def patch(self, request):
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        updated = service.update(str(user["_id"]), request.data)
        log_activity(
            "AUTHENTICATION", "PROFILE_UPDATE",
            str(request.user["_id"]), str(request.user["_id"]),
            "SUCCESS", "User updated their profile.",
        )
        return success("Profile updated successfully.", data=UserSerializer(updated).data)


@method_decorator(never_cache, name="dispatch")
class ProfileImageView(APIView):
    """Handle profile image uploads."""

    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        file = request.FILES.get("profile_image")
        if not file:
            return error("No file uploaded.", status_code=status.HTTP_400_BAD_REQUEST)
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        image_service = ProfileImageService()
        try:
            image_service.upload(str(user["_id"]), file)
        except ValueError as exc:
            return error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        updated = service.get_by_id(str(user["_id"]))
        log_activity(
            "AUTHENTICATION", "PROFILE_IMAGE_UPDATE",
            str(user["_id"]), str(user["_id"]),
            "SUCCESS", "User updated their profile image.",
        )
        return success("Profile image uploaded successfully.", data=UserSerializer(updated).data)


def serve_profile_image(request, user_id):
    """Serve a user's profile image from MongoDB GridFS."""
    if not user_id:
        return HttpResponse("Not found", status=404)

    image_service = ProfileImageService()

    users_collection = get_collection(Collections.USERS)
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return HttpResponse("Not found", status=404)

    if not user:
        return HttpResponse("Not found", status=404)

    file_id = user.get("profile_image_id")
    if not file_id:
        return HttpResponse("Not found", status=404)

    file_doc = image_service.get(file_id)
    if not file_doc:
        return HttpResponse("Not found", status=404)

    response = HttpResponse(
        file_doc["data"],
        content_type=file_doc["content_type"],
    )
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


class GoogleLoginView(APIView):
    """Handle Google login requests."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        result = AuthService().google_login(serializer.validated_data)
        return success("Google login successful.", data=result)


class VerifyEmailView(APIView):
    """Handle email verification requests via OTP."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        result = AuthService().verify_first_login(serializer.validated_data)
        return success(
            result.get("message", "Email verified successfully."),
            data=result,
        )


class SendOTPView(APIView):
    """Send an OTP to the given email."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)

        purpose = serializer.validated_data.get("purpose")

        if purpose == OTPPurpose.FORGOT_PASSWORD:
            result = PasswordService().request_password_reset(
                serializer.validated_data["email"]
            )
            return success(result["message"], data=result)

        result = OTPService().send_otp(serializer.validated_data)
        return success(result["message"], data=result)


class VerifyOTPView(APIView):
    """Verify an OTP code."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)

        purpose = serializer.validated_data.get("purpose", OTPPurpose.DEFAULT)
        user_id = None

        if purpose == OTPPurpose.FORGOT_PASSWORD:
            result = PasswordService().verify_password_reset_otp(
                email=serializer.validated_data["email"],
                otp=serializer.validated_data["otp"],
            )
            return success(result["message"], data=result)

        if purpose in (OTPPurpose.FIRST_LOGIN, OTPPurpose.EMAIL_VERIFICATION, OTPPurpose.DEFAULT):
            result = AuthService().verify_first_login(serializer.validated_data)
            user_id = result.get("user_id")
            return success(result.get("message", "OTP verified successfully."), data=result)

        service = OTPService()
        result = service.verify_otp(serializer.validated_data)
        return success(result["message"], data=result)


class ChangePasswordView(APIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        current_password = request.data.get("current_password") or request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not current_password or not new_password:
            return error(
                "current_password and new_password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        result = PasswordService().change_password(
            user_id=str(request.user["_id"]),
            current_password=current_password,
            new_password=new_password,
        )
        return success(result["message"])


class SetPasswordView(APIView):
    """Set password for Google users using OTP."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        if not otp or not new_password:
            return error(
                "otp and new_password are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        email = request.data.get("email")
        if not email:
            return error("Email is required.", status_code=status.HTTP_400_BAD_REQUEST)
        OTPService().verify_otp({
            "email": email,
            "otp": otp,
            "purpose": OTPPurpose.PASSWORD_SETUP,
        })
        user = UserService().get_by_email(email)
        PasswordService().set_password(str(user["_id"]), new_password)
        return success("Password set successfully.")


class ForgotPasswordView(APIView):
    """Send a password reset OTP to the user's registered email."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        result = PasswordService().request_password_reset(serializer.validated_data["email"])
        return success(result["message"], data=result)


class ResetPasswordView(APIView):
    """Reset the password using the single-use reset token."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if not data.get("password") and data.get("new_password"):
            data["password"] = data.get("new_password")

        serializer = ResetPasswordSerializer(data=data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)

        result = PasswordService().reset_password(
            reset_token=serializer.validated_data["reset_token"],
            new_password=serializer.validated_data["password"],
        )
        return success(result["message"])
