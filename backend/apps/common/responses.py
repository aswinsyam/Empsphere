"""
Simple response helpers.

Every successful API response uses the shape::

    {"success": True, "message": "...", "data":  {...}}

Every error response uses::

    {"success": False, "message": "..."}

Use ``success(message, data)`` and ``error(message, status_code)``
to keep responses consistent across every view.
"""

from rest_framework.response import Response
from rest_framework import status


def success(message="Success.", data=None, status_code=status.HTTP_200_OK):
    """Return a standardized success response."""
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code,
    )


def error(message="Something went wrong.", status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    """Return a standardized error response."""
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)
