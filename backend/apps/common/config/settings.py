"""
Application configuration.

Loads all environment variables from the .env file and exposes
them through a single settings object.

Every module in the project should import configuration from here
instead of calling os.getenv() directly.
"""

from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Load project .env so module-level reads of os.getenv() pick up values
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


def _get_env(key: str, default: str = "") -> str:
    """Return an env value, falling back to default when missing or empty."""
    value = os.getenv(key, default)
    return value if value not in (None, "") else default


def _get_int_env(key: str, default: int) -> int:
    """Return an env value as int, falling back to default when invalid."""
    try:
        return int(_get_env(key, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    """Application settings."""

    SECRET_KEY: str
    DEBUG: bool

    MONGO_URI: str
    DATABASE_NAME: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXP_MINUTES: int
    REFRESH_TOKEN_EXP_DAYS: int

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_USE_TLS: bool

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    COMPANY_REGISTRATION_SECRET: str

    FRONTEND_URL: str
    BACKEND_URL: str


settings = Settings(
    SECRET_KEY=os.getenv("SECRET_KEY", ""),
    DEBUG=os.getenv("DEBUG", "True") == "True",

    MONGO_URI=_get_env("MONGO_URI", "mongodb://localhost:27017"),
    DATABASE_NAME=_get_env("DATABASE_NAME", "empsphere_db"),

    JWT_SECRET=os.getenv("JWT_SECRET", ""),
    JWT_ALGORITHM=_get_env("JWT_ALGORITHM", "HS256"),
    ACCESS_TOKEN_EXP_MINUTES=_get_int_env("ACCESS_TOKEN_EXP_MINUTES", 30),
    REFRESH_TOKEN_EXP_DAYS=_get_int_env("REFRESH_TOKEN_EXP_DAYS", 7),

    EMAIL_HOST=_get_env("EMAIL_HOST", ""),
    EMAIL_PORT=_get_int_env("EMAIL_PORT", 587),
    EMAIL_HOST_USER=_get_env("EMAIL_HOST_USER", ""),
    EMAIL_HOST_PASSWORD=_get_env("EMAIL_HOST_PASSWORD", ""),
    EMAIL_USE_TLS=os.getenv("EMAIL_USE_TLS", "True") == "True",

    GOOGLE_CLIENT_ID=_get_env("GOOGLE_CLIENT_ID", ""),
    GOOGLE_CLIENT_SECRET=_get_env("GOOGLE_CLIENT_SECRET", ""),
    GOOGLE_REDIRECT_URI=_get_env("GOOGLE_REDIRECT_URI", ""),

    RAZORPAY_KEY_ID=_get_env("RAZORPAY_KEY_ID", ""),
    RAZORPAY_KEY_SECRET=_get_env("RAZORPAY_KEY_SECRET", ""),

    COMPANY_REGISTRATION_SECRET=_get_env("COMPANY_REGISTRATION_SECRET", ""),

    FRONTEND_URL=_get_env("FRONTEND_URL", "http://localhost:3000"),
    BACKEND_URL=_get_env("BACKEND_URL", "http://localhost:8000"),
)
