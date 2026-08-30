"""
Organization app URL routes.

Maps department and designation endpoints to their controllers.
"""

from django.urls import path

from apps.organization.controllers.department_controller import (
    DepartmentController,
)
from apps.organization.controllers.designation_controller import (
    DesignationController,
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
    path(
        "designations/",
        DesignationController.as_view(),
        name="designation-list-create",
    ),
    path(
        "designations/<str:designation_id>/",
        DesignationController.as_view(),
        name="designation-detail",
    ),
]
