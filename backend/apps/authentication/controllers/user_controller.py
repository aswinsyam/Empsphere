"""
User Management Controllers.

Consolidated API endpoints for user administration
(creating Admin/HR Manager/Employee accounts).
"""

from rest_framework import status
from rest_framework.views import APIView

from apps.authentication.dtos.user_dto import CreateUserDTO
from apps.authentication.serializers.user_serializer import CreateUserSerializer
from apps.authentication.services.user_service import CreateUserService
from apps.common.base.base_controller import BaseController


class CreateUserController(APIView, BaseController):
    """
    Endpoint for a privileged user to create an Admin, HR Manager,
    or Employee account.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_user_service = CreateUserService()

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        data.setdefault("phone", "")

        dto = CreateUserDTO(
            **data,
            created_by=str(request.user["_id"]),
        )

        user_id = self.create_user_service.create_user(
            dto,
            actor_role=request.user.get("role", ""),
        )

        return self.success(
            message="User created successfully.",
            data={"user_id": user_id},
            status_code=status.HTTP_201_CREATED,
        )
