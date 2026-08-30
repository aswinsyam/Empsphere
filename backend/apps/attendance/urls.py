"""
Attendance app URL routes.
"""
from django.urls import path

from apps.attendance.controllers.attendance_controller import (
    AttendanceController,
    AttendanceSummaryController,
)

urlpatterns = [
    path(
        "",
        AttendanceController.as_view(),
        name="attendance-list-create",
    ),
    path(
        "<str:attendance_id>/",
        AttendanceController.as_view(),
        name="attendance-detail",
    ),
    path(
        "actions/<str:action>/",
        AttendanceController.as_view(),
        name="attendance-action",
    ),
    path(
        "summary/<str:employee_id>/",
        AttendanceSummaryController.as_view(),
        name="attendance-summary",
    ),
]
