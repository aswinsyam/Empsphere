"""
Authentication DTOs.
Data transfer objects for authentication.
"""
from __future__ import annotations


class RegisterDTO:
    """Registration data transfer object."""

    def __init__(self, first_name, last_name, email, password,
                 confirm_password, company_secret, phone=None,
                 department_id=None, designation_id=None, created_by=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.company_secret = company_secret
        self.phone = phone
        self.department_id = department_id
        self.designation_id = designation_id
        self.created_by = created_by


class LoginDTO:
    """Login data transfer object."""

    def __init__(self, email, password):
        self.email = email
        self.password = password


class GoogleLoginDTO:
    """Google login data transfer object."""

    def __init__(self, id_token):
        self.id_token = id_token