"""
Default values used across the application.
"""

from datetime import timedelta

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Security defaults
DEFAULT_ACCESS_TOKEN_EXP = timedelta(minutes=30)
DEFAULT_REFRESH_TOKEN_EXP = timedelta(days=7)
OTP_EXPIRY_MINUTES = 10
PASSWORD_RESET_TOKEN_EXP_MINUTES = 30

# Roles
DEFAULT_ROLE = "EMPLOYEE"

# File upload
MAX_UPLOAD_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp")
ALLOWED_DOCUMENT_EXTENSIONS = ("pdf", "doc", "docx", "xls", "xlsx")

# Default org
DEFAULT_ORGANIZATION_NAME = "EmpSphere"
