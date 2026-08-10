"""
Reusable API Response.

Provides a consistent response structure across the application.
"""

from rest_framework.response import Response

from apps.common.core.status import StatusCode


class ApiResponse:
    """Standard API response builder."""

    @staticmethod
    def success(
        message: str,
        data=None,
        status_code: int = StatusCode.OK,
        meta: dict = None,
    ):
        """
        Success response.

        Example:
        {
            "success": true,
            "message": "...",
            "data": {},
            "meta": {}
        }
        """

        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "meta": meta,
            },
            status=status_code,
        )

    @staticmethod
    def error(
        message: str,
        errors=None,
        status_code: int = StatusCode.BAD_REQUEST,
    ):
        """
        Error response.

        Example:
        {
            "success": false,
            "message": "...",
            "errors": {}
        }
        """

        return Response(
            {
                "success": False,
                "message": message,
                "errors": errors,
            },
            status=status_code,
        )

    @staticmethod
    def paginated(
        message: str,
        data,
        page: int,
        page_size: int,
        total_records: int,
        status_code: int = StatusCode.OK,
    ):
        """
        Standard paginated response.
        """

        total_pages = (
            (total_records + page_size - 1) // page_size
            if page_size
            else 1
        )

        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "meta": {
                    "page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages,
                },
            },
            status=status_code,
        )