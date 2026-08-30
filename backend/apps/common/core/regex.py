"""
Centralized validation patterns.

Serializers and validators should reuse these patterns instead of
re-declaring their own regular expressions, so the backend and the
frontend enforce exactly the same rules.
"""

import re

#: Password policy: at least 8 characters, one lowercase letter,
#: one uppercase letter and one digit.
#: Mirrored by ``getPasswordRequirements()`` in ``frontend/src/utils/helpers.ts``.
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

#: Human readable description of :data:`PASSWORD_REGEX`.
PASSWORD_RULE_MESSAGE = (
    "Password must be at least 8 characters and include an uppercase letter, "
    "a lowercase letter, and a number."
)

#: Basic email shape check for values that are not validated by an
#: ``EmailField`` (e.g. raw request payloads).
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
