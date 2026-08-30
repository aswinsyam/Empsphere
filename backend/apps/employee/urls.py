"""
Employee app URL routes.
"""
from django.urls import path

from apps.employee.controllers.employee_controller import (
    EmployeeController,
)

urlpatterns = [
    path(
        "",
        EmployeeController.as_view(),
        name="employee-list-create",
    ),
    path(
        "<str:employee_id>/",
        EmployeeController.as_view(),
        name="employee-detail",
    ),
]
