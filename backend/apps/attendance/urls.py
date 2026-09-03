from django.urls import path

from apps.attendance.views import (
    AttendanceView,
    AttendanceSummaryView,
)

urlpatterns = [
    path(
        "",
        AttendanceView.as_view(),
        name="attendance-list-create",
    ),
    path(
        "<str:attendance_id>/",
        AttendanceView.as_view(),
        name="attendance-detail",
    ),
    path(
        "actions/<str:action>/",
        AttendanceView.as_view(),
        name="attendance-action",
    ),
    path(
        "summary/<str:employee_id>/",
        AttendanceSummaryView.as_view(),
        name="attendance-summary",
    ),
]
