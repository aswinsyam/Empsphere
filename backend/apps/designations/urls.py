"""
Designations app URL routes.
"""
from django.urls import path

from apps.designations.views import DesignationView

urlpatterns = [
    path("", DesignationView.as_view(), name="designation-list-create"),
    path("<str:designation_id>/", DesignationView.as_view(), name="designation-detail"),
]
