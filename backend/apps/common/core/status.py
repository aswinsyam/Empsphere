"""
HTTP status code constants.

Semantic names for HTTP status codes used across the application.
"""

from rest_framework import status as http_status


class StatusCode:
    """Application HTTP status codes."""

    # ==========================================================
    # Success
    # ==========================================================

    OK = http_status.HTTP_200_OK
    CREATED = http_status.HTTP_201_CREATED
    ACCEPTED = http_status.HTTP_202_ACCEPTED
    NO_CONTENT = http_status.HTTP_204_NO_CONTENT

    # ==========================================================
    # Client Errors
    # ==========================================================

    BAD_REQUEST = http_status.HTTP_400_BAD_REQUEST
    UNAUTHORIZED = http_status.HTTP_401_UNAUTHORIZED
    PAYMENT_REQUIRED = http_status.HTTP_402_PAYMENT_REQUIRED
    FORBIDDEN = http_status.HTTP_403_FORBIDDEN
    NOT_FOUND = http_status.HTTP_404_NOT_FOUND
    METHOD_NOT_ALLOWED = http_status.HTTP_405_METHOD_NOT_ALLOWED
    NOT_ACCEPTABLE = http_status.HTTP_406_NOT_ACCEPTABLE
    CONFLICT = http_status.HTTP_409_CONFLICT
    GONE = http_status.HTTP_410_GONE
    UNSUPPORTED_MEDIA_TYPE = http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    UNPROCESSABLE_ENTITY = http_status.HTTP_422_UNPROCESSABLE_ENTITY
    TOO_MANY_REQUESTS = http_status.HTTP_429_TOO_MANY_REQUESTS

    # ==========================================================
    # Server Errors
    # ==========================================================

    INTERNAL_SERVER_ERROR = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    NOT_IMPLEMENTED = http_status.HTTP_501_NOT_IMPLEMENTED
    BAD_GATEWAY = http_status.HTTP_502_BAD_GATEWAY
    SERVICE_UNAVAILABLE = http_status.HTTP_503_SERVICE_UNAVAILABLE
    GATEWAY_TIMEOUT = http_status.HTTP_504_GATEWAY_TIMEOUT