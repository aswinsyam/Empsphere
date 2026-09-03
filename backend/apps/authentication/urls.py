"""
Authentication API URL routes.

All authentication endpoints are mounted under /api/auth/ (see config/urls.py).
"""

from django.urls import path

from apps.authentication.views import (
    ChangePasswordView,
    ForgotPasswordView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    ProfileImageView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    SendOTPView,
    SetPasswordView,
    UserView,
    VerifyEmailView,
    VerifyOTPView,
    serve_profile_image,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("me/", UserView.as_view(), name="me"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),

    path("profile/", UserView.as_view(), name="profile"),
    path("profile/image/", ProfileImageView.as_view(), name="profile-image"),
    path("profile/image/<str:user_id>/", serve_profile_image, name="profile-image-user"),

    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("set-password/", SetPasswordView.as_view(), name="set-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
