"""
User Management Services.

Consolidated business logic for user administration
(creating Admin/HR Manager/Employee accounts).
"""

from apps.authentication.dtos.user_dto import CreateUserDTO
from apps.authentication.managers.employee_code_manager import EmployeeCodeManager
from apps.authentication.managers.password_manager import PasswordManager
from apps.authentication.repositories.user_repository import UserRepository
from apps.authentication.schemas.user_schema import UserSchema
from apps.authentication.validators.user_validator import validate_target_role
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    ForbiddenException,
)
from apps.common.permissions.role_permission import RolePermission


class CreateUserService(BaseService):
    """
    Creates a new user (Admin/HR Manager/Employee) on behalf of a
    privileged account. The caller must have sufficient privilege to
    create the requested target role.
    """

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()
        self.password_manager = PasswordManager()
        self.employee_code_manager = EmployeeCodeManager()

    def create_user(self, dto: CreateUserDTO, actor_role: str) -> str:
        """
        Create a new user with the given role.

        Uses the centralized ``RolePermission.can_assign_role`` helper to
        enforce the role hierarchy (SUPER_ADMIN → all, ADMIN → HR + Employee,
        HR → Employee, Employee → none).

        Raises:
            ForbiddenException: if the actor lacks privilege to create the role.
            ConflictException: if the email is already registered.
        """
        target_role = validate_target_role(dto.role)

        if not RolePermission.can_assign_role(actor_role, target_role):
            raise ForbiddenException(
                "You do not have permission to create a user with this role."
            )

        if self.user_repository.email_exists(dto.email):
            raise ConflictException("An account with this email already exists.")

        employee_code = self.employee_code_manager.generate()
        hashed_password = self.password_manager.hash_password(dto.password)

        document = UserSchema.create_document(
            {
                "employee_code": employee_code,
                "first_name": dto.first_name,
                "last_name": dto.last_name,
                "full_name": dto.full_name,
                "email": dto.email,
                "phone": dto.phone,
                "password": hashed_password,
                "role": target_role,
                "department_id": dto.department_id,
                "designation_id": dto.designation_id,
                "created_by": dto.created_by,
            }
        )

        user_id = self.user_repository.create(document, user_id=dto.created_by)

        self.log_activity(
            module="USER_MANAGEMENT",
            action="CREATE_USER",
            performed_by=dto.created_by,
            target_id=user_id,
            status="SUCCESS",
            description=f"Created user with role {target_role}",
        )

        return user_id
