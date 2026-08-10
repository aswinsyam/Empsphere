"""
Authentication API URL routes.

All authentication endpoints are mounted under /api/auth/ (see config/urls.py).
"""

from django.urls import path

from apps.authentication.controllers.auth_controller import (
    GoogleLoginController,
    LoginController,
    LogoutController,
    MeController,
    ProfileController,
    RefreshTokenController,
    RegisterController,
    VerifyEmailController,
)
from apps.authentication.controllers.otp_controller import (
    SendOTPController,
    VerifyOTPController,
)
from apps.authentication.controllers.password_controller import (
    ChangePasswordController,
    ForgotPasswordController,
    ResetPasswordController,
    SetPasswordController,
)
from apps.authentication.controllers.user_controller import CreateUserController

urlpatterns = [
    # Authentication
    path("register/", RegisterController.as_view(), name="register"),
    path("login/", LoginController.as_view(), name="login"),
    path("logout/", LogoutController.as_view(), name="logout"),
    path("refresh-token/", RefreshTokenController.as_view(), name="refresh-token"),
    path("me/", MeController.as_view(), name="me"),
    path("verify-email/", VerifyEmailController.as_view(), name="verify-email"),
    path("google-login/", GoogleLoginController.as_view(), name="google-login"),

    # Profile
    path("profile/", ProfileController.as_view(), name="profile"),

    # OTP
    path("send-otp/", SendOTPController.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPController.as_view(), name="verify-otp"),

    # Password
    path("change-password/", ChangePasswordController.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordController.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordController.as_view(), name="reset-password"),
    path("set-password/", SetPasswordController.as_view(), name="set-password"),

    # User management
    path("users/create/", CreateUserController.as_view(), name="create-user"),
]