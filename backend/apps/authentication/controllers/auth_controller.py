"""
Authentication Controllers.

Consolidated API endpoints for core authentication flows:
register, login, logout, me, refresh-token, verify-email, google-login,
and profile management (update + image upload).
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.authentication.dtos.auth_dto import (
    GoogleLoginDTO,
    LoginDTO,
    RegisterDTO,
    UpdateProfileDTO,
)
from apps.authentication.serializers.auth_serializer import (
    GoogleLoginSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
)
from apps.authentication.services.auth_service import (
    GoogleLoginService,
    LoginService,
    LogoutService,
    MeService,
    RefreshTokenService,
    RegisterService,
    UpdateProfileService,
    UploadProfileImageService,
    VerifyEmailService,
)
from apps.common.base.base_controller import BaseController
from apps.common.exceptions.custom_exception import ValidationException


# ==========================================================
# Register
# ==========================================================

class RegisterController(APIView, BaseController):
    """Endpoint for employee self-registration."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_service = RegisterService()

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        data.setdefault("phone", "")

        dto = RegisterDTO(**data)

        user_id = self.register_service.register(dto)

        return self.success(
            message="Registration successful.",
            data={"user_id": user_id},
            status_code=status.HTTP_201_CREATED,
        )


# ==========================================================
# Login
# ==========================================================

class LoginController(APIView, BaseController):
    """Endpoint for user login."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_service = LoginService()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = LoginDTO(**serializer.validated_data)

        result = self.login_service.login(dto)

        return self.success(
            message="Login successful.",
            data=result,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Logout
# ==========================================================

class LogoutController(APIView, BaseController):
    """Endpoint to revoke the current refresh token."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_service = LogoutService()

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.logout_service.logout(serializer.validated_data["refresh_token"])

        return self.success(
            message="Logged out successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Me
# ==========================================================

class MeController(APIView, BaseController):
    """Endpoint returning the current authenticated user profile."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.me_service = MeService()

    def get(self, request):
        user_id = str(request.user["_id"])

        profile = self.me_service.get_profile(user_id)

        return self.success(
            message="Profile fetched successfully.",
            data=profile,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Refresh Token
# ==========================================================

class RefreshTokenController(APIView, BaseController):
    """Endpoint to issue a fresh access token from a refresh token."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_token_service = RefreshTokenService()

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        result = self.refresh_token_service.refresh(
            serializer.validated_data["refresh_token"]
        )

        return self.success(
            message="Token refreshed successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Verify Email
# ==========================================================

class VerifyEmailController(APIView, BaseController):
    """Endpoint to verify a user's email address."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verify_email_service = VerifyEmailService()

    def post(self, request):
        token = request.data.get("token", "")

        self.verify_email_service.verify_email(token)

        return self.success(
            message="Email verified successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Google Login
# ==========================================================

class GoogleLoginController(APIView, BaseController):
    """Endpoint for Google OAuth2 login."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_login_service = GoogleLoginService()

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = GoogleLoginDTO(**serializer.validated_data)

        result = self.google_login_service.google_login(dto)

        return self.success(
            message="Google login successful.",
            data=result,
            status_code=status.HTTP_200_OK,
        )


# ==========================================================
# Profile (Update + Image Upload)
# ==========================================================

class ProfileController(APIView, BaseController):
    """
    Endpoints for the current user's profile management: update editable
    fields and upload a profile image. Only the authenticated owner may
    access these endpoints (enforced by the default IsAuthenticatedUser).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_profile_service = UpdateProfileService()
        self.upload_profile_image_service = UploadProfileImageService()

    def patch(self, request):
        """Update the current user's editable profile fields."""
        serializer = UpdateProfileSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        dto = UpdateProfileDTO(
            **serializer.validated_data,
            user_id=str(request.user["_id"]),
        )

        profile = self.update_profile_service.update_profile(dto)

        return self.success(
            message="Profile updated successfully.",
            data=profile,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        """Upload the current user's profile image."""
        uploaded_file = request.FILES.get("profile_image")

        if not uploaded_file:
            raise ValidationException("A profile_image file is required.")

        profile = self.upload_profile_image_service.upload(
            str(request.user["_id"]),
            uploaded_file,
        )

        return self.success(
            message="Profile image uploaded successfully.",
            data=profile,
            status_code=status.HTTP_200_OK,
        )
