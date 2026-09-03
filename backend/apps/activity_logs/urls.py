"""
Activity Log URL routes.
"""
from django.urls import path

from apps.activity_logs.views import ActivityLogView, get_distinct_actions

urlpatterns = [
    path("", ActivityLogView.as_view(), name="activity-log-list"),
    path("actions/", get_distinct_actions, name="activity-log-actions"),
]
