"""
Custom application exceptions.

These exceptions are raised throughout the application for
business logic, validation, authentication, authorization,
and resource-related errors.

The global exception handler converts them into a standard
API response.
"""

from apps.common.core.messages import Messages
from apps.common.core.status import StatusCode


class CustomException(Exception):
    """
    Base application exception.
    """

    def __init__(
        self,
        message: str,
        errors=None,
        status_code: int = StatusCode.BAD_REQUEST,
    ):
        super().__init__(message)
        self.message = message
        self.errors = errors
        self.status_code = status_code


# ==========================================================
# Validation
# ==========================================================

class ValidationException(CustomException):
    """Raised when request validation fails."""

    def __init__(
        self,
        message=Messages.VALIDATION_ERROR,
        errors=None,
    ):
        super().__init__(
            message=message,
            errors=errors,
            status_code=StatusCode.BAD_REQUEST,
        )


# ==========================================================
# Authentication
# ==========================================================

class UnauthorizedException(CustomException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message=Messages.UNAUTHORIZED,
    ):
        super().__init__(
            message=message,
            status_code=StatusCode.UNAUTHORIZED,
        )


# ==========================================================
# Authorization
# ==========================================================

class ForbiddenException(CustomException):
    """Raised when permission is denied."""

    def __init__(
        self,
        message=Messages.FORBIDDEN,
    ):
        super().__init__(
            message=message,
            status_code=StatusCode.FORBIDDEN,
        )


# ==========================================================
# Resource Not Found
# ==========================================================

class NotFoundException(CustomException):
    """Raised when a resource cannot be found."""

    def __init__(
        self,
        message=Messages.NOT_FOUND,
    ):
        super().__init__(
            message=message,
            status_code=StatusCode.NOT_FOUND,
        )


# ==========================================================
# Duplicate Resource
# ==========================================================

class ConflictException(CustomException):
    """Raised when a duplicate resource exists."""

    def __init__(
        self,
        message=Messages.DUPLICATE_RECORD,
    ):
        super().__init__(
            message=message,
            status_code=StatusCode.CONFLICT,
        )


# ==========================================================
# Internal Server Error
# ==========================================================

class InternalServerException(CustomException):
    """Raised for unexpected server errors."""

    def __init__(
        self,
        message=Messages.INTERNAL_ERROR,
    ):
        super().__init__(
            message=message,
            status_code=StatusCode.INTERNAL_SERVER_ERROR,
        )