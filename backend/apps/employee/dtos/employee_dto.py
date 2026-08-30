"""
Employee DTOs.
Data transfer objects for employee management.
"""
from __future__ import annotations


class EmployeeDTO:
    """Employee data transfer object used during creation."""

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password=None,
        phone=None,
        role="EMPLOYEE",
        department_id=None,
        designation_id=None,
        joining_date=None,
        status="ACTIVE",
        employee_code=None,
        created_by=None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone
        self.role = role
        self.department_id = department_id
        self.designation_id = designation_id
        self.joining_date = joining_date
        self.status = status
        self.employee_code = employee_code
        self.created_by = created_by


class EmployeeUpdateDTO:
    """Employee data transfer object used during update."""

    def __init__(
        self,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        role=None,
        department_id=None,
        designation_id=None,
        joining_date=None,
        status=None,
        employee_code=None,
        updated_by=None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.role = role
        self.department_id = department_id
        self.designation_id = designation_id
        self.joining_date = joining_date
        self.status = status
        self.employee_code = employee_code
        self.updated_by = updated_by
