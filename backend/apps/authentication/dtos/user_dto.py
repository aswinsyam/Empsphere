"""
User DTOs.
Data transfer objects for user.
"""
from __future__ import annotations


class CreateUserDTO:
    """Create user data transfer object."""

    def __init__(self, first_name, last_name, email, password,
                 confirm_password, company_secret, phone=None,
                 role="EMPLOYEE", department_id=None,
                 designation_id=None, created_by=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.company_secret = company_secret
        self.phone = phone
        self.role = role
        self.department_id = department_id
        self.designation_id = designation_id
        self.created_by = created_by


class UpdateProfileDTO:
    """Update profile data transfer object."""

    def __init__(self, user_id, first_name=None, last_name=None,
                 phone=None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone