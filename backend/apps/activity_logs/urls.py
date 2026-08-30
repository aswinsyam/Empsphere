"""
Activity Log URL routes.
"""
from django.urls import path

from apps.activity_logs.views.activity_log_view import ActivityLogController, get_distinct_actions

urlpatterns = [
    path("", ActivityLogController.as_view(), name="activity-log-list"),
    path("actions/", get_distinct_actions, name="activity-log-actions"),
]
