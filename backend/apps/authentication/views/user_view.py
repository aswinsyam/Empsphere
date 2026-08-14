"""
User View.
Handles HTTP API requests for user-related operations.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.services.user_service import UserService
from apps.authentication.serializers.user_serializer import UserSerializer
from apps.common.responses.api_response import ApiResponse


class UserView(APIView):
    """Handle user-related API requests."""

    def get(self, request, user_id=None):
        service = UserService()
        if user_id:
            user = service.get_by_id(user_id)
            serializer = UserSerializer(user)
            return ApiResponse.success(
                message="User fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        users = service.get_all()
        return ApiResponse.success(
            message="Users fetched successfully.",
            data=[UserSerializer(u).data for u in users],
            status_code=status.HTTP_200_OK,
        )