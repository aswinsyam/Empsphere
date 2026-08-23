"""
User View.
Handles HTTP API requests for user-related operations.
"""
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from bson import ObjectId

from apps.authentication.services.user_service import UserService
from apps.authentication.services.profile_image_service import ProfileImageService
from apps.authentication.serializers.user_serializer import UserSerializer
from apps.common.responses.api_response import ApiResponse
from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class UserView(APIView):
    """Handle user-related API requests.

    Dispatches based on URL path:
    - /me/             -> GET current user profile
    - /profile/        -> GET/PATCH current user profile
    """

    def get(self, request):
        """Return the current authenticated user's profile."""
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        return ApiResponse.success(
            message="User fetched successfully.",
            data=UserSerializer(user).data,
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request):
        """Update the current authenticated user's profile."""
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        updates = request.data
        updated = service.update(str(user["_id"]), updates)
        service.log_activity(
            module="AUTHENTICATION",
            action="PROFILE_UPDATE",
            performed_by=str(request.user["_id"]),
            target_id=str(request.user["_id"]),
            status="SUCCESS",
            description="User updated their profile.",
        )
        return ApiResponse.success(
            message="Profile updated successfully.",
            data=UserSerializer(updated).data,
            status_code=status.HTTP_200_OK,
        )


@method_decorator(never_cache, name="dispatch")
class ProfileImageView(APIView):
    """Handle profile image uploads."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Upload a profile image for the current authenticated user."""
        file = request.FILES.get("profile_image")
        if not file:
            return ApiResponse.error(
                message="No file uploaded.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        service = UserService()
        user = service.get_by_id(str(request.user["_id"]))
        image_service = ProfileImageService()
        try:
            image_service.upload(str(user["_id"]), file)
        except ValueError as exc:
            return ApiResponse.error(
                message=str(exc),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        updated = service.get_by_id(str(user["_id"]))
        service.log_activity(
            module="AUTHENTICATION",
            action="PROFILE_IMAGE_UPDATE",
            performed_by=str(user["_id"]),
            target_id=str(user["_id"]),
            status="SUCCESS",
            description="User updated their profile image.",
        )
        return ApiResponse.success(
            message="Profile image uploaded successfully.",
            data=UserSerializer(updated).data,
            status_code=status.HTTP_200_OK,
        )


def serve_profile_image(request, user_id):
    """Serve a user's profile image from MongoDB GridFS.

    This endpoint is intentionally public because:
    - The URL contains the user's ObjectId, which is not guessable.
    - It only serves the specific profile image for the specified user.
    - It allows browser <img> tags to load avatars without JWT headers.
    """
    if not user_id:
        return HttpResponse("Not found", status=404)

    image_service = ProfileImageService()

    users_collection = mongo.get_collection(Collections.USERS)
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return HttpResponse("Not found", status=404)

    if not user:
        return HttpResponse("Not found", status=404)

    file_id = user.get("profile_image_id")
    if not file_id:
        return HttpResponse("Not found", status=404)

    file_doc = image_service.get(file_id)
    if not file_doc:
        return HttpResponse("Not found", status=404)

    response = HttpResponse(
        file_doc["data"],
        content_type=file_doc["content_type"],
    )
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
