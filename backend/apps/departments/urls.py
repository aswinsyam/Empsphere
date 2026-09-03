"""
Departments app URL routes.
"""
from django.urls import path

from apps.departments.views import DepartmentView

urlpatterns = [
    path("", DepartmentView.as_view(), name="department-list-create"),
    path("<str:department_id>/", DepartmentView.as_view(), name="department-detail"),
]
