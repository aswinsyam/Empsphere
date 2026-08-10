"""
Global exception handler.

Converts all exceptions into a standardized API response.
Registered in Django settings as the REST_FRAMEWORK EXCEPTION_HANDLER.
"""

import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response

from apps.common.exceptions.custom_exception import CustomException

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
    """Central exception handler for the whole application."""

    # Handle our custom exceptions
    if isinstance(exc, CustomException):
        return Response(
            {
                "success": False,
                "message": exc.message,
                "errors": exc.errors,
            },
            status=exc.status_code,
        )

    # Let DRF handle its own exceptions (validation, auth, etc.)
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        message = "Request validation failed."

        if response.status_code == 401:
            message = "Authentication credentials were not provided."
        elif response.status_code == 403:
            message = "You do not have permission to perform this action."
        elif response.status_code == 404:
            message = "Resource not found."

        return Response(
            {
                "success": False,
                "message": message,
                "errors": errors,
            },
            status=response.status_code,
        )

    # Unhandled exception
    logger.exception("Unhandled exception: %s", exc)

    return Response(
        {
            "success": False,
            "message": "An unexpected error occurred. Please try again.",
            "errors": None,
        },
        status=500,
    )
