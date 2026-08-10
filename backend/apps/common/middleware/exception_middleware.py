"""
Exception handling middleware.

Catches unhandled exceptions and returns a standardized JSON response.
"""

import logging

from django.http import JsonResponse

logger = logging.getLogger("apps")


class ExceptionMiddleware:
    """Convert unhandled exceptions into a JSON error response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled error: %s", exc)

            return JsonResponse(
                {
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                    "errors": None,
                },
                status=500,
            )
