"""
User View.
Handles HTTP API requests for user-related operations.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.services.user_service import UserService
from apps.authentication.serializers.user_serializer import UserSerializer
from apps.authentication.serializers.auth_serializer import AuthSerializer
from apps.common.responses.api_response import ApiResponse


class UserView(APIView):
    """Handle user-related API requests.

    Dispatches based on URL path:
    - /me/             -> GET current user profile
    - /profile/        -> GET/PATCH current user profile
    - /users/create/   -> POST create a new user
    """

    def get(self, request):
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        return ApiResponse.success(
            message="User fetched successfully.",
            data=UserSerializer(user).data,
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request):
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        updates = request.data
        updated = service.update(str(user["_id"]), updates)
        return ApiResponse.success(
            message="Profile updated successfully.",
            data=UserSerializer(updated).data,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid():
            service = UserService()
            result = service.create(serializer.validated_data, user_id=str(request.user["_id"]))
            return ApiResponse.success(
                message="User created successfully.",
                data={"user_id": str(result)},
                status_code=status.HTTP_201_CREATED,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ProfileImageView(APIView):
    """Handle profile image uploads."""

    def post(self, request):
        file = request.FILES.get("profile_image")
        if not file:
            return ApiResponse.error(
                message="No file uploaded.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        # Save uploaded file under MEDIA_ROOT/profiles/
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        filename = default_storage.save(
            os.path.join("profiles", file.name),
            ContentFile(file.read()),
        )
        file_url = f"/media/{filename}"
        updated = service.update_profile_image(str(user["_id"]), file_url)
        return ApiResponse.success(
            message="Profile image uploaded successfully.",
            data=UserSerializer(updated).data,
            status_code=status.HTTP_200_OK,
        )
