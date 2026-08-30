"""
Payment Controller.
Exposes RESTful endpoints for office payment management.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.common.config.settings import settings
from apps.payment.dtos.payment_dto import PaymentCreateDTO, PaymentVerifyDTO
from apps.payment.serializers.payment_serializer import (
    PaymentCreateSerializer,
    PaymentVerifySerializer,
)
from apps.payment.services.payment_service import PaymentService


class PaymentController(APIView, BaseController):
    """Office payment endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role(Role.SUPER_ADMIN, Role.ADMIN, Role.HR_MANAGER, Role.EMPLOYEE)
    def post(self, request):
        """Create a new office payment and Cashfree order."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_role = request.user.get("role")
        user_id = str(request.user["_id"])
        amenity_id = serializer.validated_data["amenity_id"]

        employee_id = serializer.validated_data.get("employee_id")

        if user_role == "EMPLOYEE":
            employee_id = user_id
        elif not employee_id:
            if user_role == "SUPER_ADMIN":
                return self.error(
                    message="Employee is required.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            employee_id = user_id

        dto = PaymentCreateDTO(
            employee_id=employee_id,
            amenity_id=amenity_id,
            paid_by=user_id,
            created_by=user_id,
        )

        result = self.payment_service.create_payment(dto)

        return self.success(
            message="Payment initiated successfully.",
            data=result,
            status_code=status.HTTP_201_CREATED,
        )

    @require_role(Role.SUPER_ADMIN, Role.ADMIN, Role.HR_MANAGER, Role.EMPLOYEE)
    def get(self, request, payment_id=None):
        """List payments, get a single payment, or get current user's payments."""
        url_name = request.resolver_match.url_name
        if url_name == "payment-me":
            return self._get_my_payments(request)

        user_role = request.user.get("role")
        user_id = str(request.user["_id"])

        if payment_id:
            payment = self.payment_service.get_payment(payment_id)
            if user_role == "EMPLOYEE" and payment.get("employee_id") != user_id:
                return self.error(
                    message="You do not have permission to view this payment.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return self.success(
                message="Payment fetched successfully.",
                data=payment,
                status_code=status.HTTP_200_OK,
            )

        employee_id = request.query_params.get("employee_id")
        department_id = request.query_params.get("department_id")
        amenity_id = request.query_params.get("amenity_id")
        status_filter = request.query_params.get("status")
        date = request.query_params.get("date")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if user_role == "EMPLOYEE":
            employee_id = user_id
            department_id = None
            amenity_id = None

        result = self.payment_service.list_payments(
            employee_id=employee_id,
            department_id=department_id,
            amenity_id=amenity_id,
            status=status_filter,
            date=date,
            page=page,
            page_size=page_size,
        )
        return self.success(
            message="Payments fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    def _get_my_payments(self, request):
        """Get current user's payments."""
        user_id = str(request.user["_id"])
        status_filter = request.query_params.get("status")
        date = request.query_params.get("date")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        result = self.payment_service.list_payments(
            employee_id=user_id,
            status=status_filter,
            date=date,
            page=page,
            page_size=page_size,
        )
        return self.success(
            message="My payments fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )


class PaymentVerifyController(APIView, BaseController):
    """Payment verification endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role(Role.SUPER_ADMIN, Role.ADMIN, Role.HR_MANAGER, Role.EMPLOYEE)
    def post(self, request, payment_id):
        """Verify Cashfree payment status."""
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = PaymentVerifyDTO(
            gateway_order_id=serializer.validated_data["gateway_order_id"],
            gateway_payment_id=serializer.validated_data["gateway_payment_id"],
            payment_status=serializer.validated_data.get("payment_status"),
        )

        payment = self.payment_service.verify_payment(
            payment_id, dto, user_id=str(request.user["_id"])
        )

        return self.success(
            message="Payment verified successfully.",
            data=payment,
            status_code=status.HTTP_200_OK,
        )


class PaymentCancelController(APIView, BaseController):
    """Payment cancellation endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role(Role.SUPER_ADMIN, Role.ADMIN, Role.HR_MANAGER, Role.EMPLOYEE)
    def post(self, request, payment_id):
        """Cancel a pending payment."""
        user_role = request.user.get("role")
        user_id = str(request.user["_id"])

        payment = self.payment_service.get_payment(payment_id)

        if user_role == "EMPLOYEE" and payment.get("employee_id") != user_id:
            return self.error(
                message="You do not have permission to cancel this payment.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        payment = self.payment_service.cancel_payment(
            payment_id, user_id=user_id
        )

        return self.success(
            message="Payment cancelled successfully.",
            data=payment,
            status_code=status.HTTP_200_OK,
        )
