"""
Centralized application messages.

All user-facing success and error messages should be defined here.
"""

class Messages:
    """Application messages."""

    # ==========================================================
    # Authentication
    # ==========================================================

    REGISTER_SUCCESS = "Account registered successfully."
    LOGIN_SUCCESS = "Login successful."
    LOGOUT_SUCCESS = "Logged out successfully."

    TOKEN_REFRESHED = "Access token refreshed successfully."

    PASSWORD_CHANGED = "Password changed successfully."

    EMAIL_VERIFIED = "Email verified successfully."
    EMAIL_VERIFICATION_SENT = "Verification email sent successfully."

    OTP_SENT = "OTP sent successfully."
    OTP_VERIFIED = "OTP verified successfully."

    GOOGLE_LOGIN_SUCCESS = "Google login successful."

    # ==========================================================
    # User
    # ==========================================================

    USER_CREATED = "User created successfully."
    USER_UPDATED = "User updated successfully."
    USER_DELETED = "User deleted successfully."
    USER_FETCHED = "User fetched successfully."

    # ==========================================================
    # Employee
    # ==========================================================

    EMPLOYEE_CREATED = "Employee created successfully."
    EMPLOYEE_UPDATED = "Employee updated successfully."
    EMPLOYEE_DELETED = "Employee deleted successfully."
    EMPLOYEE_FETCHED = "Employee details fetched successfully."

    # ==========================================================
    # Department
    # ==========================================================

    DEPARTMENT_CREATED = "Department created successfully."
    DEPARTMENT_UPDATED = "Department updated successfully."
    DEPARTMENT_DELETED = "Department deleted successfully."

    # ==========================================================
    # Organization
    # ==========================================================

    ORGANIZATION_CREATED = "Organization created successfully."
    ORGANIZATION_UPDATED = "Organization updated successfully."

    # ==========================================================
    # Attendance
    # ==========================================================

    ATTENDANCE_MARKED = "Attendance marked successfully."
    ATTENDANCE_UPDATED = "Attendance updated successfully."

    # ==========================================================
    # Leave
    # ==========================================================

    LEAVE_APPLIED = "Leave request submitted successfully."
    LEAVE_APPROVED = "Leave approved successfully."
    LEAVE_REJECTED = "Leave rejected successfully."

    # ==========================================================
    # Payment
    # ==========================================================

    PAYMENT_CREATED = "Payment initiated successfully."
    PAYMENT_VERIFIED = "Payment verified successfully."
    PAYMENT_FAILED = "Payment failed."
    PAYMENT_CANCELLED = "Payment cancelled successfully."
    PAYMENT_PENDING = "Payment is pending."

    # ==========================================================
    # Notification
    # ==========================================================

    NOTIFICATION_SENT = "Notification sent successfully."

    # ==========================================================
    # Generic Success
    # ==========================================================

    CREATED = "Created successfully."
    UPDATED = "Updated successfully."
    DELETED = "Deleted successfully."
    FETCHED = "Data fetched successfully."

    # ==========================================================
    # Authentication Errors
    # ==========================================================

    INVALID_CREDENTIALS = "Invalid email or password."
    ACCOUNT_INACTIVE = "Your account has been deactivated."
    ACCOUNT_DELETED = "Your account has been deleted."
    EMAIL_ALREADY_EXISTS = "Email already exists."
    EMAIL_NOT_VERIFIED = "Please verify your email first."

    INVALID_PASSWORD = "Password is incorrect."
    INVALID_OLD_PASSWORD = "Current password is incorrect."

    INVALID_TOKEN = "Invalid or expired token."
    TOKEN_EXPIRED = "Session expired. Please login again."

    INVALID_OTP = "Invalid OTP."
    OTP_EXPIRED = "OTP has expired."

    # ==========================================================
    # Authorization
    # ==========================================================

    UNAUTHORIZED = "Authentication credentials were not provided."
    FORBIDDEN = "You do not have permission to perform this action."

    # ==========================================================
    # Validation
    # ==========================================================

    VALIDATION_ERROR = "Validation failed."
    INVALID_REQUEST = "Invalid request."

    # ==========================================================
    # Common Errors
    # ==========================================================

    NOT_FOUND = "Requested resource not found."
    USER_NOT_FOUND = "User not found."
    EMPLOYEE_NOT_FOUND = "Employee not found."
    DEPARTMENT_NOT_FOUND = "Department not found."
    ROLE_NOT_FOUND = "Role not found."

    DUPLICATE_RECORD = "Record already exists."

    INTERNAL_ERROR = "An unexpected error occurred."
    SERVER_ERROR = "Internal server error."

    # ==========================================================
    # File Upload
    # ==========================================================

    FILE_UPLOADED = "File uploaded successfully."
    FILE_DELETED = "File deleted successfully."