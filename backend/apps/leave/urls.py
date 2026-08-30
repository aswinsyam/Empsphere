"""
Leave app URL routes.
"""
from django.urls import path

from apps.leave.controllers.leave_controller import (
    LeaveController,
)

urlpatterns = [
    path(
        "",
        LeaveController.as_view(),
        name="leave-list-create",
    ),
    path(
        "<str:leave_id>/",
        LeaveController.as_view(),
        name="leave-detail",
    ),
]
