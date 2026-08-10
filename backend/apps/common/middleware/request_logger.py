"""
Request logging middleware.

Logs incoming requests and their response status.
"""

import logging
import time

logger = logging.getLogger("apps")


class RequestLoggerMiddleware:
    """Logs each request with method, path, status and duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()

        response = self.get_response(request)

        duration = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.path,
            response.status_code,
            duration,
        )

        return response
