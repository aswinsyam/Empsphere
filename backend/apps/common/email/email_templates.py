"""
Email template names.

Centralized template name constants used with EmailService.
"""


class EmailTemplates:
    """Template paths for rendered email bodies."""

    VERIFY_EMAIL = "emails/verify_email.html"
    FORGOT_PASSWORD = "emails/forgot_password.html"
    OTP = "emails/otp_email.html"
    WELCOME = "emails/welcome.html"
