from django.urls import path

from apps.leaves.views import LeaveView

urlpatterns = [
    path(
        "",
        LeaveView.as_view(),
        name="leave-list-create",
    ),
    path(
        "<str:leave_id>/",
        LeaveView.as_view(),
        name="leave-detail",
    ),
]
