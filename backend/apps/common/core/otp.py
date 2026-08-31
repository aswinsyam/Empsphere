"""
Centralized OTP purposes and OTP policy constants.

Every OTP that is created or verified must declare a purpose so that an
OTP issued for one flow can never be replayed in another one (for
example a login/email-verification OTP can not be used to reset a
password).

Repositories, services and serializers should use these constants
instead of hardcoding purpose strings.
"""


class OTPPurpose:
    """Supported OTP purposes."""

    EMAIL_VERIFICATION = "email_verification"
    FIRST_LOGIN = "first_login"
    PASSWORD_SETUP = "password_setup"
    FORGOT_PASSWORD = "forgot_password"

    #: Every purpose accepted by the OTP endpoints.
    ALL = (
        EMAIL_VERIFICATION,
        FIRST_LOGIN,
        PASSWORD_SETUP,
        FORGOT_PASSWORD,
    )

    #: Default purpose kept for backwards compatibility with existing clients.
    DEFAULT = EMAIL_VERIFICATION


# ==========================================================
# OTP policy
# ==========================================================

#: Number of digits in a generated OTP code.
OTP_LENGTH = 6

#: How long an OTP stays valid after it has been generated.
OTP_EXPIRY_MINUTES = 10
