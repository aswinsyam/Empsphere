"""
Base Controller.

Provides reusable API response methods.
"""

from rest_framework import status

from apps.common.responses.api_response import ApiResponse


class BaseController:
    """
    Base controller for all API controllers.
    """

    @staticmethod
    def success(
        message: str,
        data=None,
        status_code=status.HTTP_200_OK,
    ):
        return ApiResponse.success(
            message=message,
            data=data,
            status_code=status_code,
        )

    @staticmethod
    def error(
        message: str,
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        return ApiResponse.error(
            message=message,
            errors=errors,
            status_code=status_code,
        )
