"""
Shared regular expressions used for validation.
"""

import re

# Email address (basic but practical)
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Password: at least 8 chars, one uppercase, one lowercase, one digit
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

# Phone: 10-15 digits, optional leading +
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{9,14}$")

# A simple alphanumeric identifier (e.g. employee code)
CODE_REGEX = re.compile(r"^[A-Z0-9_-]+$")

# ObjectId hex string
OBJECT_ID_REGEX = re.compile(r"^[0-9a-fA-F]{24}$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value))


def is_valid_password(value: str) -> bool:
    return bool(PASSWORD_REGEX.match(value))


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_REGEX.match(value))
