"""
Organization app URL routes.
"""

from django.urls import path

from apps.organization.controllers.department_controller import (
    DepartmentController,
)

urlpatterns = [
    path(
        "departments/",
        DepartmentController.as_view(),
        name="department-list-create",
    ),
    path(
        "departments/<str:department_id>/",
        DepartmentController.as_view(),
        name="department-detail",
    ),
]
