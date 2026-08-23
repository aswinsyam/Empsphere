"""
Authentication API URL routes.

All authentication endpoints are mounted under /api/auth/ (see config/urls.py).
"""

from django.urls import path

from apps.authentication.views.auth_view import AuthView
from apps.authentication.views.otp_view import OTPView
from apps.authentication.views.user_view import UserView, ProfileImageView, serve_profile_image
from apps.authentication.views.password_view import PasswordView
from apps.authentication.views.google_login_view import GoogleLoginView
from apps.authentication.views.verify_email_view import VerifyEmailView
from apps.authentication.views.refresh_token_view import RefreshTokenView

urlpatterns = [
    # Authentication
    path("register/", AuthView.as_view(), name="register"),
    path("login/", AuthView.as_view(), name="login"),
    path("logout/", AuthView.as_view(), name="logout"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("me/", UserView.as_view(), name="me"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),

    # Profile
    path("profile/", UserView.as_view(), name="profile"),
    path("profile/image/", ProfileImageView.as_view(), name="profile-image"),
    path("profile/image/<str:user_id>/", serve_profile_image, name="profile-image-user"),

    # OTP
    path("send-otp/", OTPView.as_view(), name="send-otp"),
    path("verify-otp/", OTPView.as_view(), name="verify-otp"),

    # Password
    path("change-password/", PasswordView.as_view(), name="change-password"),
    path("set-password/", PasswordView.as_view(), name="set-password"),
    path("forgot-password/", PasswordView.as_view(), name="forgot-password"),
    path("reset-password/", PasswordView.as_view(), name="reset-password"),
]
