from django.urls import path

from apps.employees.views import EmployeeView

urlpatterns = [
    path(
        "",
        EmployeeView.as_view(),
        name="employee-list-create",
    ),
    path(
        "<str:employee_id>/",
        EmployeeView.as_view(),
        name="employee-detail",
    ),
]
