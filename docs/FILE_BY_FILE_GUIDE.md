# File-by-File Guide

This document explains the purpose, implementation, and interactions of every active important source file in the EmpSphere codebase.

---

## Backend

### backend/manage.py

**Purpose**: Django's command-line utility entry point.

**Why this file exists**: Provides the CLI interface for running migrations, starting the dev server, and executing management commands.

**Used by**: Developers running `python manage.py runserver`, `python manage.py migrate`, `python manage.py seed_rbac`.

**Calls**: `django.core.management.execute_from_command_line(sys.argv)`

**Data flow**:
```
CLI invocation → main() sets DJANGO_SETTINGS_MODULE → Django loads config/settings.py → executes command
```

---

### backend/config/settings.py

**Purpose**: Central Django settings module.

**Why this file exists**: Every Django project needs a single settings module that configures installed apps, middleware, DRF defaults, database, CORS, email, JWT, and logging.

**Used by**: Django startup, all middleware, all DRF configuration, all apps via `apps.common.config.settings`.

**Key sections**:
- `INSTALLED_APPS` — Registers all Django apps
- `MIDDLEWARE` — CORS, security, sessions, request logging, exception handling
- `REST_FRAMEWORK` — Default auth (`JWTAuthentication`), default permission, exception handler
- `SIMPLE_JWT` — Access token lifetime (30 min), refresh token lifetime (7 days), rotation enabled
- `EMAIL_BACKEND` — SMTP configuration for OTP delivery
- `LOGGING` — Console + file handlers

---

### backend/config/urls.py

**Purpose**: Root URL router.

**Why this file exists**: Django needs a single root URL configuration that dispatches requests to app-level URL configs.

**URL patterns**:
- `/api/auth/` → `apps.authentication.urls`
- `/api/organization/` → `apps.organization.urls`
- `/api/employees/` → `apps.employee.urls`
- `/api/attendance/` → `apps.attendance.urls`
- `/api/leaves/` → `apps.leave.urls`
- `/api/activity-logs/` → `apps.activity_logs.urls`
- `/api/statistics/` → `apps.statistics.urls`
- `/api/reports/` → `apps.reports.urls`

---

### backend/apps/common/base/base_controller.py

**Purpose**: Base controller providing reusable response helpers.

**Why this file exists**: Eliminates repetitive `ApiResponse.success()` / `ApiResponse.error()` calls across views.

**Used by**: Controllers that inherit from it: `AttendanceController`, `EmployeeController`, `LeaveController`, `DepartmentController`, `DesignationController`, `ReportController`, `StatisticsController`, `ActivityLogController`.

**Classes**:
- `BaseController`:
  - `success(message, data, status_code, meta)` — Returns standardized success response
  - `error(message, errors, status_code)` — Returns standardized error response

---

### backend/apps/common/base/base_service.py

**Purpose**: Base service providing activity logging.

**Why this file exists**: All business logic services need to write audit logs. Inheriting from `BaseService` gives them access to `AuditService`.

**Used by**: Every service class in the project.

**Classes**:
- `BaseService`:
  - `__init__()` — Instantiates `AuditService`
  - `log_activity(module, action, performed_by, target_id, status, description, metadata)` — Writes audit log to MongoDB

**Data flow**:
```
Service method → self.log_activity(...) → AuditService.log() → MongoDB activity_logs collection
```

---

### backend/apps/common/responses/api_response.py

**Purpose**: Standardized API response envelope builder.

**Why this file exists**: Every API endpoint should return responses in the same format: `{ success, message, data, meta }` or `{ success, message, errors }`.

**Used by**: All controllers and views.

**Classes**:
- `ApiResponse`:
  - `success(message, data, status_code, meta)` — Returns `{ success: true, message, data, meta }`
  - `error(message, errors, status_code)` — Returns `{ success: false, message, errors }`
  - `paginated(message, data, page, page_size, total_records, status_code)` — Returns paginated response

---

### backend/apps/common/exceptions/custom_exception.py

**Purpose**: Custom exception hierarchy for application-level errors.

**Why this file exists**: Standard Python exceptions don't carry HTTP status codes. Custom exceptions allow the global exception handler to return consistent API responses.

**Used by**: All services and controllers.

**Classes**:
- `CustomException(message, errors, status_code)` — Base exception
- `ValidationException` — 400 Bad Request
- `UnauthorizedException` — 401 Unauthorized
- `ForbiddenException` — 403 Forbidden
- `NotFoundException` — 404 Not Found
- `ConflictException` — 409 Conflict
- `InternalServerException` — 500 Internal Server Error

---

### backend/apps/common/core/otp.py

**Purpose**: Centralized OTP purposes and policy constants.

**Why this file exists**: OTPs must be scoped to a specific purpose to prevent replay attacks. Hardcoding purpose strings would be error-prone.

**Used by**: `OTPService`, serializers, views.

**Constants**:
- `OTPPurpose.EMAIL_VERIFICATION = "email_verification"`
- `OTPPurpose.LOGIN = "login"`
- `OTPPurpose.FIRST_LOGIN = "first_login"`
- `OTPPurpose.PASSWORD_SETUP = "password_setup"`
- `OTPPurpose.FORGOT_PASSWORD = "forgot_password"`
- `OTP_LENGTH = 6`
- `OTP_EXPIRY_MINUTES = 10`

---

### backend/apps/common/security/password_manager.py

**Purpose**: Secure password hashing and verification using bcrypt.

**Why this file exists**: Passwords must never be stored in plaintext. This module provides a single, secure implementation.

**Used by**: `AuthService`, `PasswordService`, `EmployeeService`

**Classes**:
- `PasswordManager`:
  - `hash_password(password)` — Hashes with bcrypt, raises `ValidationException` if password exceeds 72 bytes UTF-8
  - `verify_password(plain_password, hashed_password)` — Verifies against bcrypt hash, returns `False` for invalid hashes

---

### backend/apps/common/middleware/authentication.py

**Purpose**: Custom JWT authentication for Django REST Framework.

**Why this file exists**: DRF's default JWT auth doesn't match the project's token structure. This middleware extracts Bearer tokens, validates them, and attaches the user payload.

**Used by**: DRF's authentication pipeline (registered in `settings.py`)

**Classes**:
- `JWTAuthentication(BaseAuthentication)`:
  - `authenticate(request)` — Extracts Bearer token, decodes JWT, fetches user from MongoDB
  - `authenticate_header(request)` — Returns `'Bearer realm="api"'`

**Data flow**:
```
Incoming request → extracts Bearer token → jwt.decode() → UserRepository.get_by_id() → request.user populated
```

---

### backend/apps/authentication/services/auth_service.py

**Purpose**: Core authentication business logic.

**Why this file exists**: Keeps HTTP handling separate from authentication rules. All auth flows are orchestrated here.

**Used by**: `AuthView`, `OTPView`, `VerifyEmailView`, `GoogleLoginView`, `RefreshTokenView`

**Classes**:
- `AuthService(BaseService)`:
  - `register(dto)` — Creates user, sends email verification OTP
  - `login(dto)` — Verifies credentials, issues tokens or triggers OTP
  - `verify_first_login(dto)` — Verifies OTP, marks email verified, issues tokens
  - `google_login(dto)` — Verifies Google token, creates/links user, issues tokens
  - `refresh_token(refresh_token)` — Validates refresh token, rotates it
  - `_generate_access_token(user)` — Encodes JWT with `token_type="access"`
  - `_generate_refresh_token(user)` — Encodes JWT with `token_type="refresh"`

---

### backend/apps/authentication/services/otp_service.py

**Purpose**: OTP creation, verification, and email delivery.

**Why this file exists**: OTP logic is shared across email verification, login, and password reset flows.

**Used by**: `AuthService`, `PasswordService`, `OTPView`, `PasswordView`

**Classes**:
- `OTPService(BaseService)`:
  - `send_otp(dto)` — Invalidates existing OTPs, generates 6-digit code, stores in MongoDB, sends email
  - `_generate_otp()` — Static method using `secrets.randbelow` for secure random number
  - `verify_otp(dto)` — Validates OTP matches email + purpose, not expired, not used

---

### backend/apps/authentication/services/password_service.py

**Purpose**: Password operations — change, set, forgot password, reset password.

**Why this file exists**: Password logic spans multiple flows and must be centralized.

**Used by**: `PasswordView`

**Classes**:
- `PasswordService(BaseService)`:
  - `change_password(user_id, current_password, new_password)` — Verifies current password, hashes new one
  - `set_password(user_id, new_password)` — Sets password without verifying current (for Google users)
  - `request_password_reset(email)` — Sends forgot-password OTP
  - `verify_password_reset_otp(email, otp)` — Verifies OTP, issues single-use reset token
  - `reset_password(reset_token, new_password)` — Validates reset token, hashes new password

---

### backend/apps/authentication/services/profile_image_service.py

**Purpose**: Profile image storage and retrieval using MongoDB GridFS.

**Why this file exists**: Profile images are large binary files that don't belong in the user document.

**Used by**: `ProfileImageView`, `serve_profile_image`

**Classes**:
- `ProfileImageService`:
  - `validate_file(uploaded_file)` — Checks content type and size (max 5MB)
  - `upload(user_id, uploaded_file)` — Stores file in GridFS, updates user's `profile_image_id`
  - `get(file_id)` — Retrieves GridFS file by ObjectId
  - `delete_by_user_id(user_id)` — Deletes all profile images for a user

---

### backend/apps/authentication/repositories/user_repository.py

**Purpose**: Data access layer for user documents.

**Why this file exists**: Services should not contain raw MongoDB queries.

**Used by**: `AuthService`, `PasswordService`, `EmployeeService`, `UserService`, views

**Classes**:
- `UserRepository`:
  - `email_exists(email)` — Checks if email is already registered
  - `get_by_email(email)` — Case-insensitive lookup by email
  - `get_by_id(user_id)` — Lookup by MongoDB ObjectId
  - `get_by_google_id(google_id)` — Lookup by Google ID
  - `create(document, user_id)` — Inserts new user with audit fields
  - `update(user_id, updates)` — Updates user fields
  - `soft_delete(user_id)` — Marks user as inactive

---

### backend/apps/authentication/managers/token_blacklist_manager.py

**Purpose**: JWT token blacklisting.

**Why this file exists**: When a user logs out or resets their password, their refresh token must be invalidated.

**Used by**: `AuthService`, `PasswordService`

**Classes**:
- `TokenBlacklistManager(BaseManager)`:
  - `blacklist(refresh_token)` — Stores token in blacklist collection
  - `is_blacklisted(refresh_token)` — Checks if token is blacklisted
  - `blacklist_all_user_tokens(user_id)` — Blacklists all refresh tokens for a user

---

### backend/apps/authentication/managers/password_reset_token_manager.py

**Purpose**: Issues and validates short-lived password reset tokens.

**Why this file exists**: Password reset requires a separate authorization token that is consumed after use.

**Used by**: `PasswordService`

**Classes**:
- `PasswordResetTokenManager(BaseManager)`:
  - `generate(user)` — Issues JWT with `token_type="password_reset"`
  - `verify(reset_token)` — Validates token type, purpose, expiry, and blacklist status
  - `invalidate(reset_token)` — Blacklists the token so it can never be reused

---

### backend/apps/authentication/views/auth_view.py

**Purpose**: HTTP endpoint for register, login, and logout.

**Why this file exists**: Dispatches auth requests to the correct `AuthService` method based on URL path.

**Used by**: `apps/authentication/urls.py`

**Classes**:
- `AuthView(APIView)`:
  - `post(request)` — Dispatches to `_register`, `_login`, or `_logout`

---

### backend/apps/authentication/views/otp_view.py

**Purpose**: HTTP endpoint for sending and verifying OTPs.

**Why this file exists**: OTP send/verify is a shared endpoint used by multiple auth flows.

**Used by**: `apps/authentication/urls.py`

**Classes**:
- `OTPView(APIView, BaseController)`:
  - `post(request)` — Dispatches to send or verify based on URL name

---

### backend/apps/employee/services/employee_service.py

**Purpose**: Employee business logic — create, read, update, delete, status toggle.

**Why this file exists**: Employee operations involve validation, role checks, activity logging, and serialization.

**Used by**: `EmployeeController`, `ReportService`

**Classes**:
- `EmployeeService(BaseService)`:
  - `create_employee(dto)` — Validates, hashes password, creates document
  - `get_employee(employee_id)` — Fetches and serializes single employee
  - `list_employees(...)` — Paginated, filtered list
  - `update_employee(employee_id, dto, actor_role)` — Partial update with role check
  - `delete_employee(employee_id, user_id)` — Soft delete
  - `update_employee_status(employee_id, status, user_id, actor_role)` — Toggle active/inactive

---

### backend/apps/employee/repositories/employee_repository.py

**Purpose**: Data access layer for employee documents (stored in users collection).

**Why this file exists**: Employees are stored in the same MongoDB collection as users. This repository adds employee-specific query methods.

**Used by**: `EmployeeService`

**Classes**:
- `EmployeeRepository`:
  - `get_all(search, department_id, status, page, page_size, ...)` — Paginated query with regex search
  - `create(document, user_id)` — Delegates to `UserRepository.create()`
  - `get_by_id(employee_id)` — Validates ObjectId, delegates to `UserRepository`
  - `update(employee_id, updates, user_id)` — Delegates to `UserRepository`
  - `soft_delete(employee_id, user_id)` — Delegates to `UserRepository`

---

### backend/apps/attendance/services/attendance_service.py

**Purpose**: Attendance business logic — mark, check-in, check-out, update, summary.

**Why this file exists**: Attendance rules (duplicate prevention, self-access, inactive checks) must be enforced consistently.

**Used by**: `AttendanceController`, `ReportService`

**Classes**:
- `AttendanceService(BaseService)`:
  - `mark_attendance(dto, user_role)` — Validates, prevents duplicates, creates record
  - `check_in(employee_id, user_role)` — Creates or updates attendance for today
  - `check_out(employee_id, user_role)` — Validates check-in exists, sets check-out timestamp
  - `get_attendance_summary(employee_id, start_date, end_date)` — Counts present/absent/half_day/leave days

---

### backend/apps/leave/services/leave_service.py

**Purpose**: Leave business logic — apply, get, list, approve/reject.

**Why this file exists**: Leave workflows involve date validation, self-application checks, and status transitions.

**Used by**: `LeaveController`, `ReportService`

**Classes**:
- `LeaveService(BaseService)`:
  - `apply_leave(dto, user_role)` — Validates dates and type, creates PENDING leave
  - `list_leaves(employee_id, status, leave_type, start_date, end_date, page, page_size)` — Paginated, filtered list
  - `update_leave_status(leave_id, status, user_id)` — Approves or rejects pending leave

---

### backend/apps/organization/services/department_service.py

**Purpose**: Department business logic — create, read, update, delete, list.

**Why this file exists**: Departments need duplicate name/code checks, employee count tracking, and activity logging.

**Used by**: `DepartmentController`, `ReportService`

**Classes**:
- `DepartmentService(BaseService)`:
  - `create_department(dto)` — Validates, checks duplicates, creates
  - `list_departments(search, page, page_size, include_inactive)` — Paginated, filtered list
  - `update_department(department_id, dto, actor_role)` — Partial update with duplicate checks
  - `delete_department(department_id, user_id, actor_role)` — Soft delete after checking no employees assigned

---

### backend/apps/organization/services/designation_service.py

**Purpose**: Designation business logic — create, read, update, list.

**Why this file exists**: Designations need duplicate name/code checks and activity logging.

**Used by**: `DesignationController`, `ReportService`

**Classes**:
- `DesignationService(BaseService)`:
  - `create_designation(dto)` — Validates, checks duplicates, creates
  - `list_designations(search, page, page_size, include_inactive)` — Paginated, filtered list
  - `update_designation(designation_id, dto)` — Partial update

---

### backend/apps/activity_logs/services/audit_service.py

**Purpose**: Writes audit log entries to MongoDB.

**Why this file exists**: Activity logging is cross-cutting. Centralizing it ensures all services log in the same format.

**Used by**: `BaseService.log_activity()` in every service

**Classes**:
- `AuditService`:
  - `log(module, action, performed_by, target_id, status, description, metadata)` — Inserts document into `activity_logs` collection

---

### backend/apps/activity_logs/views/activity_log_view.py

**Purpose**: HTTP endpoints for retrieving activity logs with role-based filtering.

**Why this file exists**: Provides a read-only API for activity logs.

**Used by**: `apps/activity_logs/urls.py`

**Classes/Functions**:
- `ActivityLogController(APIView, BaseController)`:
  - `get(request)` — Lists activity logs with module/action/user filters, role-scoped results
- `get_distinct_actions(request)` — Returns sorted distinct action values

---

### backend/apps/statistics/services/statistics_service.py

**Purpose**: Aggregates dashboard statistics counts.

**Why this file exists**: Dashboard needs summary counts from multiple collections.

**Used by**: `StatisticsController`

**Classes**:
- `StatisticsService`:
  - `get_dashboard_stats()` — Returns counts from users, departments, attendance, and leaves

---

### backend/apps/reports/services/report_service.py

**Purpose**: Orchestrates report generation by combining summaries and paginated records.

**Why this file exists**: Reports need aggregated summaries plus detailed records from multiple services.

**Used by**: `ReportController`

**Classes**:
- `ReportService(BaseService)`:
  - `get_employee_report(filters)` — Employee summary + paginated list
  - `get_attendance_report(filters)` — Attendance summary + paginated list
  - `get_leave_report(filters)` — Leave summary + paginated list
  - `get_department_report(filters)` — Department summary + list with employee counts
  - `get_designation_report(filters)` — Designation summary + list with employee counts
  - `get_activity_report(filters)` — Activity summary + paginated log records

---

### backend/apps/common/database/mongo.py

**Purpose**: MongoDB connection manager (singleton).

**Why this file exists**: All database access needs a single MongoDB client connection.

**Used by**: Every repository and schema class.

**Classes**:
- `MongoConnection`:
  - `get_collection(collection_name)` — Returns a MongoDB collection
- `mongo = MongoConnection()` — Singleton instance

---

### backend/apps/common/decorators/permission.py

**Purpose**: Role-based permission decorator for APIView methods.

**Why this file exists**: Restricts view methods to specific roles without repeating permission logic.

**Used by**: All controllers that need role-based access.

**Functions**:
- `require_role(*allowed_roles)` — Decorator that allows only the given roles to access the view

---

### backend/apps/common/security/google_manager.py

**Purpose**: Google OAuth2 authentication helper.

**Why this file exists**: Validates Google ID tokens and extracts user info for Google login flow.

**Used by**: `AuthService.google_login()`

**Classes**:
- `GoogleManager`:
  - `verify_id_token(token)` — Verifies Google ID token, returns decoded claims
  - `extract_user_info(info)` — Extracts normalized user fields from Google claims

---

### backend/templates/emails/otp_email.html

**Purpose**: HTML email template for OTP delivery.

**Why this file exists**: Provides a branded, responsive email template for OTP codes.

**Used by**: `OTPService._send_otp_email()`

**Variables**: `otp` (the code), `year` (current year), `purpose` (determines heading text)

---

## Backend: Payroll & Payment

### backend/apps/payroll/__init__.py

**Purpose**: Payroll app package marker.

---

### backend/apps/payroll/urls.py

**Purpose**: Payroll URL routes.

**URL patterns**:
- `POST /api/payroll/` — Generate payroll
- `GET /api/payroll/` — List payrolls
- `GET /api/payroll/{id}/` — Retrieve payroll
- `PUT /api/payroll/{id}/` — Update payroll
- `POST /api/payroll/{id}/approve/` — Approve payroll
- `POST /api/payroll/{id}/cancel/` — Cancel payroll
- `GET /api/payroll/me/` — Current employee's payrolls

---

### backend/apps/payroll/dtos/payroll_dto.py

**Purpose**: Data transfer objects for payroll create/update.

**Used by**: `PayrollController`

**Classes**:
- `PayrollDTO` — employee_id, payroll_period, basic_salary, allowances, deductions, created_by
- `PayrollUpdateDTO` — basic_salary, allowances, deductions, updated_by

---

### backend/apps/payroll/serializers/payroll_serializer.py

**Purpose**: DRF serializers for payroll validation.

**Used by**: `PayrollController`

**Classes**:
- `PayrollSerializer` — Validates create payload
- `PayrollUpdateSerializer` — Validates update payload

---

### backend/apps/payroll/validators/payroll_validator.py

**Purpose**: Payroll validation logic.

**Used by**: `PayrollService`

**Classes**:
- `PayrollValidator`:
  - `validate_create(employee_id, payroll_period, basic_salary)` — Ensures required fields and non-negative salary
  - `validate_update(update_data)` — Ensures update data is not empty

---

### backend/apps/payroll/repositories/payroll_repository.py

**Purpose**: Data access layer for payroll documents.

**Used by**: `PayrollService`

**Classes**:
- `PayrollRepository`:
  - `_ensure_indexes()` — Creates unique index on `(employee_id, payroll_period)`
  - `create(document, user_id)` — Inserts payroll record
  - `get_by_id(payroll_id)` — Fetches by ObjectId
  - `get_by_employee_and_period(employee_id, payroll_period)` — Checks for duplicates
  - `get_all(...)` — Paginated query with filters
  - `update(payroll_id, updates, user_id)` — Partial update
  - `soft_delete(payroll_id, user_id)` — Soft delete

---

### backend/apps/payroll/services/payroll_service.py

**Purpose**: Payroll business logic and orchestration.

**Used by**: `PayrollController`

**Classes**:
- `PayrollService(BaseService)`:
  - `create_payroll(dto)` — Validates employee, checks duplicates, computes gross/net salary, creates payroll
  - `get_payroll(payroll_id)` — Retrieves single payroll
  - `list_payrolls(...)` — Lists with filters and pagination
  - `update_payroll(payroll_id, dto, user_id)` — Updates GENERATED payroll only
  - `approve_payroll(payroll_id, user_id)` — Transitions to APPROVED
  - `cancel_payroll(payroll_id, user_id)` — Transitions to CANCELLED

**Calculations**:
- `gross_salary = basic_salary + allowances`
- `net_salary = gross_salary - deductions`

---

### backend/apps/payroll/controllers/payroll_controller.py

**Purpose**: HTTP endpoints for payroll management.

**Used by**: `apps/payroll/urls.py`

**Classes**:
- `PayrollController(APIView, BaseController)`:
  - `post(request)` — Create payroll or approve/cancel via URL name dispatch
  - `get(request)` — List or retrieve payroll (EMPLOYEE restricted to own records)
  - `_get_my_payrolls(request)` — Returns current user's payrolls via `/me/` endpoint
  - `put(request, payroll_id)` — Update GENERATED payroll

---

### backend/apps/payment/__init__.py

**Purpose**: Payment app package marker.

---

### backend/apps/payment/urls.py

**Purpose**: Payment URL routes.

**URL patterns**:
- `POST /api/payment/` — Create payment
- `GET /api/payment/` — List payments
- `GET /api/payment/{id}/` — Retrieve payment
- `PUT /api/payment/{id}/` — Update payment status
- `GET /api/payment/me/` — Current employee's payments

---

### backend/apps/payment/dtos/payment_dto.py

**Purpose**: Data transfer objects for payment create/update.

**Used by**: `PaymentController`

**Classes**:
- `PaymentDTO` — payroll_id, employee_id, amount, payment_date, payment_reference, notes, created_by
- `PaymentUpdateDTO` — status, payment_reference, notes, updated_by

---

### backend/apps/payment/serializers/payment_serializer.py

**Purpose**: DRF serializers for payment validation.

**Used by**: `PaymentController`

**Classes**:
- `PaymentSerializer` — Validates create payload
- `PaymentUpdateSerializer` — Validates update payload

---

### backend/apps/payment/validators/payment_validator.py

**Purpose**: Payment validation logic.

**Used by**: `PaymentService`

**Classes**:
- `PaymentValidator`:
  - `validate_create(payroll_id, employee_id, amount)` — Ensures positive amount
  - `validate_status(status)` — Validates status is PENDING/PAID/FAILED/CANCELLED

---

### backend/apps/payment/repositories/payment_repository.py

**Purpose**: Data access layer for payment documents.

**Used by**: `PaymentService`

**Classes**:
- `PaymentRepository`:
  - `_ensure_indexes()` — Creates unique index on `payroll_id`
  - `create(document, user_id)` — Inserts payment record
  - `get_by_id(payment_id)` — Fetches by ObjectId
  - `get_by_payroll_id(payroll_id)` — Fetches by payroll reference
  - `get_all(...)` — Paginated query with filters
  - `update(payment_id, updates, user_id)` — Partial update
  - `soft_delete(payment_id, user_id)` — Soft delete

---

### backend/apps/payment/services/payment_service.py

**Purpose**: Payment business logic and orchestration.

**Used by**: `PaymentController`

**Classes**:
- `PaymentService(BaseService)`:
  - `create_payment(dto)` — Validates payroll exists, matches employee, amount == net_salary, creates payment
  - `get_payment(payment_id)` — Retrieves single payment
  - `list_payments(...)` — Lists with filters and pagination
  - `update_payment_status(payment_id, dto, user_id)` — Updates status with transition validation

---

### backend/apps/payment/controllers/payment_controller.py

**Purpose**: HTTP endpoints for payment management.

**Used by**: `apps/payment/urls.py`

**Classes**:
- `PaymentController(APIView, BaseController)`:
  - `post(request)` — Create payment (MANAGER roles only)
  - `get(request)` — List or retrieve payment (EMPLOYEE restricted to own records)
  - `_get_my_payments(request)` — Returns current user's payments via `/me/` endpoint
  - `put(request, payment_id)` — Update payment status

---

## Frontend

### frontend/src/main.tsx

### frontend/src/main.tsx

**Purpose**: React entry point.

**Why this file exists**: Standard React 18 entry point using `createRoot`.

**Used by**: Vite build system

**Calls**: `ReactDOM.createRoot()`, `App`

---

### frontend/src/App.tsx

**Purpose**: Application root component.

**Why this file exists**: Composes Redux Provider, BrowserRouter, ToastProvider, AppBootstrap, and AppRoutes.

**Used by**: `main.tsx`

**Calls**: `Provider`, `BrowserRouter`, `ToastProvider`, `AppBootstrap`, `AppRoutes`

---

### frontend/src/routes/AppRoutes.tsx

**Purpose**: Central route definitions with auth and role guards.

**Why this file exists**: Single source of truth for all application routes.

**Used by**: `App.tsx`

**Route structure**:
- Public routes: `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email`, `/set-password`, `/change-password`, `/unauthorized`
- Protected routes nested under `ProtectedRoute` → `DashboardLayout`
- Role-specific dashboards guarded by `RequireRole`

---

### frontend/src/components/AppBootstrap.tsx

**Purpose**: Session restoration on app load.

**Why this file exists**: After a page refresh, Redux state is lost but JWT token remains in localStorage. This component re-fetches the user profile.

**Used by**: `App.tsx`

**Flow**:
```
Component mounts → checks for access token → dispatches fetchMe → user state restored or redirected to login
```

---

### frontend/src/config/axios.ts

**Purpose**: Configured Axios instance with interceptors.

**Why this file exists**: Centralizes HTTP client configuration — base URL, auth headers, token refresh, error handling.

**Used by**: All `services/*.ts` files, `AppBootstrap.tsx`

**Key features**:
1. Request interceptor: Attaches Bearer token except for public endpoints
2. Response interceptor: On 401, attempts token refresh once before retrying
3. On refresh failure: Clears tokens and dispatches `auth:expired` event

---

### frontend/src/store/slices/authSlice.ts

**Purpose**: Redux slice for authentication state and async thunks.

**Why this file exists**: Centralizes auth state and all auth-related API calls.

**Used by**: `AppBootstrap.tsx`, `VerifyEmailForm.tsx`, `ProfilePage.tsx`, auth middleware

**State shape**: `{ user, accessToken, refreshToken, loading, error }`

**Thunks**: `login`, `register`, `fetchMe`, `logoutUser`, `googleLogin`, `completeFirstLogin`

---

### frontend/src/hooks/useAuth.ts

**Purpose**: Custom hook exposing auth selectors and actions.

**Why this file exists**: Encapsulates Redux store access so pages don't directly import store internals.

**Used by**: All auth pages, `ProtectedRoute`, `RequireRole`, `Navbar`, `Sidebar`, dashboard pages

**Returns**: `{ user, accessToken, refreshToken, loading, error, login, register, logoutUser, ... }`

---

### frontend/src/services/api.ts

**Purpose**: Generic HTTP wrapper with typed methods.

**Why this file exists**: All API services should use the same request/response pattern.

**Used by**: All `services/*.ts` files

**Methods**: `get<T>`, `post<T>`, `put<T>`, `patch<T>`, `delete<T>` — all return `Promise<T>` by unwrapping `response.data`

---

### frontend/src/utils/helpers.ts

**Purpose**: Generic utility helpers.

**Why this file exists**: Pure helper functions with no framework dependencies.

**Used by**: Many components and pages

**Exports**:
- `getPasswordRequirements(password)` — Returns password strength checks
- `cn(...classes)` — Simple class-name joiner
- `formatDate(value)` — Formats ISO date string
- `formatDateTime(value)` — Formats ISO datetime string
- `getErrorMessage(error)` — Extracts human-friendly error message from API error
- `getProfileImageUrl(userId, version)` — Constructs GridFS profile image URL

---

### frontend/src/utils/constants.ts

**Purpose**: Application-wide constants.

**Why this file exists**: Centralizes role definitions, route paths, and navigation items.

**Used by**: 21+ files

**Exports**: `ROLES`, `EMPLOYEE_MANAGER_ROLES`, `canManageEmployees`, `ROUTES`, `ROLE_DASHBOARD_ROUTES`, `getDashboardRoute`, `APP_NAME`, `getNavItems`

---

### frontend/src/utils/token.ts

**Purpose**: localStorage wrapper for JWT tokens.

**Why this file exists**: Centralizes token access so the rest of the app doesn't directly manipulate localStorage keys.

**Used by**: Axios interceptors, auth slice, AppBootstrap

**Exports**: `TokenUtil.getAccessToken()`, `TokenUtil.getRefreshToken()`, `TokenUtil.setTokens()`, `TokenUtil.clear()`

---

### frontend/src/components/common/Button.tsx

**Purpose**: Reusable button component with variants and loading state.

**Why this file exists**: Every page uses buttons. Centralizing ensures consistency.

**Used by**: 21+ components and pages

**Props**: `children`, `variant` (primary/ghost/danger), `loading`, `disabled`, `type`, `onClick`, `className`

---

### frontend/src/components/common/Modal.tsx

**Purpose**: Accessible dialog component.

**Why this file exists**: Forms across the app need modals. Centralizing prevents bugs.

**Used by**: All form modals, `DepartmentsPage`, `LeavesPage`, `DesignationsPage`

**Props**: `open`, `title`, `onClose`, `children`, `size`

---

### frontend/src/components/common/Pagination.tsx

**Purpose**: Previous/Next page navigation.

**Why this file exists**: All paginated list pages need the same pagination UI.

**Used by**: `EmployeesPage`, `DepartmentsPage`, `DesignationsPage`, `AttendancePage`, `LeavesPage`, `ActivityLogsPage`, `ReportsPage`

**Props**: `page`, `pageSize`, `totalRecords`, `onPageChange`, `disabled`

---

### frontend/src/components/layout/DashboardLayout.tsx

**Purpose**: Application shell — Sidebar + Navbar + content outlet.

**Why this file exists**: All protected pages share the same layout structure.

**Used by**: `AppRoutes.tsx`

**Calls**: `Sidebar`, `Navbar`, `Outlet`

---

### frontend/src/components/auth/LoginForm.tsx

**Purpose**: Login form with email/password and Google login.

**Why this file exists**: Encapsulates login form logic so `LoginPage` stays thin.

**Used by**: `LoginPage.tsx`

**Calls**: `useAuth`, `GoogleAuthButton`, `Button`, `Input`

---

### frontend/src/pages/dashboard/AdminDashboardPage.tsx

**Purpose**: Admin role dashboard.

**Why this file exists**: Each role sees a different dashboard with role-specific stats.

**Used by**: `AppRoutes.tsx`

**Calls**: `DashboardContent`, `statisticsService`, `activityLogService`, `useDashboardData`

**Data flow**:
```
Component mounts → useDashboardData() → Promise.all([stats, activities]) → DashboardContent renders
```

---

### backend/apps/attendance/dtos/attendance_dto.py

**Purpose**: Data transfer objects for attendance create/update.

**Why this file exists**: DTOs keep controller validation separate from service logic.

**Used by**: `AttendanceController`

**Classes**:
- `AttendanceDTO` — employee_id, date, status, check_in, check_out, remarks, created_by
- `AttendanceUpdateDTO` — status, check_in, check_out, remarks, updated_by

---

### backend/apps/attendance/repositories/attendance_repository.py

**Purpose**: Data access layer for attendance documents.

**Why this file exists**: Encapsulates MongoDB queries and ensures the unique employee-date index exists.

**Used by**: `AttendanceService`

**Classes**:
- `AttendanceRepository`:
  - `_ensure_indexes()` — Creates unique index on `(employee_id, date)` to prevent duplicate attendance entries
  - `create(document, user_id)` — Inserts attendance record
  - `get_by_id(attendance_id)` — Fetches by ObjectId
  - `get_by_employee_and_date(employee_id, date)` — Looks up today's record for check-in/out
  - `get_all(...)` — Paginated query with date range and status filters
  - `update(attendance_id, updates, user_id)` — Partial update

---

### backend/apps/attendance/serializers/attendance_serializer.py

**Purpose**: DRF serializers for attendance validation.

**Why this file exists**: Validates attendance payloads, including check-in/check-out time ordering.

**Used by**: `AttendanceController`

**Classes**:
- `AttendanceSerializer` — Validates create payload
- `AttendanceUpdateSerializer` — Validates update payload
- `CheckInSerializer` — No fields, action-only endpoint
- `CheckOutSerializer` — No fields, action-only endpoint

**Validation**: Cross-field check that `check_in < check_out` when both are provided.

---

### backend/apps/attendance/urls.py

**Purpose**: Attendance URL routes.

**URL patterns**:
- `POST /api/attendance/` — Mark attendance
- `GET /api/attendance/` — List attendance
- `GET /api/attendance/<id>/` — Get single attendance
- `PUT /api/attendance/<id>/` — Update attendance
- `POST /api/attendance/actions/check-in/` — Check in
- `POST /api/attendance/actions/check-out/` — Check out
- `GET /api/attendance/summary/<employee_id>/` — Attendance summary

---

### backend/apps/employee/dtos/employee_dto.py

**Purpose**: Data transfer objects for employee create/update.

**Why this file exists**: Separates request validation from service business logic.

**Used by**: `EmployeeController`

**Classes**:
- `EmployeeDTO` — first_name, last_name, email, password, phone, role, department_id, designation_id, joining_date, status, employee_code, created_by
- `EmployeeUpdateDTO` — Same fields minus password, plus updated_by

---

### backend/apps/employee/repositories/employee_repository.py

**Purpose**: Data access layer for employee documents (users collection).

**Why this file exists**: Adds employee-specific queries on top of `UserRepository`.

**Used by**: `EmployeeService`

**Classes**:
- `EmployeeRepository`:
  - `create(document, user_id)` — Delegates to `UserRepository.create()`
  - `get_by_id(employee_id)` — Validates ObjectId, delegates to `UserRepository`
  - `get_by_email(email)` — Delegates to `UserRepository`
  - `get_all(search, department_id, status, page, page_size, joining_date_from, joining_date_to)` — Regex search across name, email, code, phone with date range filters
  - `update(employee_id, updates, user_id)` — Delegates to `UserRepository`
  - `soft_delete(employee_id, user_id)` — Delegates to `UserRepository`

---

### backend/apps/employee/serializers/employee_serializer.py

**Purpose**: DRF serializer for employee validation.

**Why this file exists**: Centralizes employee field validation including phone regex.

**Used by**: `EmployeeController`

**Classes**:
- `EmployeeSerializer` — Validates all employee fields; `is_create=True` makes first_name, last_name, email, role, password required

---

### backend/apps/employee/urls.py

**Purpose**: Employee URL routes.

**URL patterns**:
- `POST /api/employees/` — Create employee
- `GET /api/employees/` — List employees
- `GET /api/employees/<id>/` — Get employee
- `PUT /api/employees/<id>/` — Update employee
- `PATCH /api/employees/<id>/` — Update employee status
- `DELETE /api/employees/<id>/` — Delete employee (SUPER_ADMIN only)

---

### backend/apps/leave/dtos/leave_dto.py

**Purpose**: Data transfer objects for leave create.

**Why this file exists**: Separates request validation from service logic.

**Used by**: `LeaveController`

**Classes**:
- `LeaveDTO` — employee_id, start_date, end_date, leave_type, reason, status, created_by

---

### backend/apps/leave/repositories/leave_repository.py

**Purpose**: Data access layer for leave documents.

**Why this file exists**: Encapsulates MongoDB queries for the leaves collection.

**Used by**: `LeaveService`

**Classes**:
- `LeaveRepository`:
  - `create(document, user_id)` — Inserts leave record
  - `get_by_id(leave_id)` — Fetches by ObjectId
  - `get_all(employee_id, status, leave_type, start_date, end_date, page, page_size)` — Paginated query with date overlap logic
  - `update(leave_id, updates, user_id)` — Partial update

---

### backend/apps/leave/serializers/leave_serializer.py

**Purpose**: DRF serializers for leave validation.

**Why this file exists**: Validates leave create/update payloads and shapes read responses.

**Used by**: `LeaveController`

**Classes**:
- `LeaveSerializer` — Validates start_date, end_date, leave_type, reason
- `LeaveDetailSerializer` — Shapes read response with employee_name, employee_code, approved_by, rejected_by

---

### backend/apps/leave/urls.py

**Purpose**: Leave URL routes.

**URL patterns**:
- `POST /api/leaves/` — Apply for leave
- `GET /api/leaves/` — List leaves
- `GET /api/leaves/<id>/` — Get single leave
- `PUT /api/leaves/<id>/` — Approve/reject leave

---

### backend/apps/organization/controllers/designation_controller.py

**Purpose**: HTTP endpoints for designation CRUD.

**Why this file exists**: Dispatches designation requests to `DesignationService`.

**Used by**: `apps/organization/urls.py`

**Classes**:
- `DesignationController(APIView, BaseController)`:
  - `post(request)` — Creates designation (EMPLOYEE_MANAGER_ROLES)
  - `get(request, designation_id)` — Lists or gets designation
  - `put(request, designation_id)` — Updates designation

---

### backend/apps/organization/dtos/designation_dto.py

**Purpose**: Data transfer objects for designation create/update.

**Why this file exists**: Separates request validation from service logic.

**Used by**: `DesignationController`

**Classes**:
- `DesignationDTO` — name, code, description, created_by
- `DesignationUpdateDTO` — name, code, description, is_active, updated_by

---

### backend/apps/organization/serializers/designation_serializer.py

**Purpose**: DRF serializers for designation validation.

**Why this file exists**: Validates designation payloads.

**Used by**: `DesignationController`

**Classes**:
- `DesignationSerializer` — Validates create payload
- `DesignationUpdateSerializer` — Validates update payload (all fields optional)

---

### backend/apps/organization/validators/designation_validator.py

**Purpose**: Designation validation logic.

**Why this file exists**: Centralizes validation rules for designations.

**Used by**: `DesignationService`

**Classes**:
- `DesignationValidator`:
  - `validate_create(name, code)` — Ensures name is not empty
  - `validate_update(designation_id, update_data)` — Ensures update data is not empty and name is not blank

---

### backend/apps/organization/repositories/designation_repository.py

**Purpose**: Data access layer for designation documents.

**Why this file exists**: Encapsulates MongoDB queries for designations.

**Used by**: `DesignationService`

**Classes**:
- `DesignationRepository`:
  - `create(document, user_id)` — Inserts designation
  - `get_by_id(designation_id)` — Fetches by ObjectId
  - `get_all(search, page, page_size, include_inactive)` — Paginated query with regex search
  - `update(designation_id, updates, user_id)` — Partial update

---

### backend/apps/organization/urls.py

**Purpose**: Organization URL routes.

**URL patterns**:
- `GET/POST /api/organization/departments/` — List/create departments
- `GET/PUT/DELETE /api/organization/departments/<id>/` — Department detail
- `GET/POST /api/organization/designations/` — List/create designations
- `GET/PUT /api/organization/designations/<id>/` — Designation detail

---

### backend/apps/statistics/controllers/statistics_controller.py

**Purpose**: HTTP endpoint for dashboard statistics.

**Why this file exists**: Returns aggregated counts for the dashboard.

**Used by**: `apps/statistics/urls.py`

**Classes**:
- `StatisticsController(APIView, BaseController)`:
  - `get(request)` — Returns dashboard stats for all roles

---

### backend/apps/statistics/serializers/statistics_serializer.py

**Purpose**: DRF serializer for statistics response.

**Why this file exists**: Shapes the statistics response payload.

**Used by**: `StatisticsController`

---

### backend/apps/statistics/urls.py

**Purpose**: Statistics URL routes.

**URL patterns**:
- `GET /api/statistics/` — Dashboard statistics

---

### backend/apps/reports/controllers/report_controller.py

**Purpose**: HTTP endpoints for report generation.

**Why this file exists**: Dispatches report requests to `ReportService` based on URL path.

**Used by**: `apps/reports/urls.py`

**Classes**:
- `ReportController(APIView, BaseController)`:
  - `get(request)` — Dispatches to employee, attendance, leave, department, designation, or activity report based on URL suffix

---

### backend/apps/reports/serializers/report_serializer.py

**Purpose**: DRF serializers for report responses.

**Why this file exists**: Shapes report response payloads.

**Used by**: `ReportController`

---

### backend/apps/reports/urls.py

**Purpose**: Reports URL routes.

**URL patterns**:
- `GET /api/reports/employees/` — Employee report
- `GET /api/reports/attendance/` — Attendance report
- `GET /api/reports/leaves/` — Leave report
- `GET /api/reports/departments/` — Department report
- `GET /api/reports/designations/` — Designation report
- `GET /api/reports/activity/` — Activity report

---

### backend/apps/activity_logs/urls.py

**Purpose**: Activity log URL routes.

**URL patterns**:
- `GET /api/activity-logs/` — List activity logs
- `GET /api/activity-logs/actions/` — Distinct actions

---

### backend/apps/common/core/regex.py

**Purpose**: Centralized validation regex patterns.

**Why this file exists**: Ensures backend and frontend enforce identical validation rules.

**Used by**: Serializers, validators, and mirrored by `getPasswordRequirements()` in frontend.

**Constants**:
- `PASSWORD_REGEX` — At least 8 chars, one uppercase, one lowercase, one digit
- `EMAIL_REGEX` — Basic email shape check

---

## Frontend

### frontend/src/components/attendance/AttendanceFormModal.tsx

**Purpose**: Reusable modal for marking attendance.

**Why this file exists**: The attendance page needs a form to create attendance records with employee, date, status, check-in/out times, and remarks.

**Used by**: `AttendancePage.tsx`

**Props**: `open`, `submitting`, `formError`, `employees`, `selectedEmployee`, `form`, `onClose`, `onSubmit`, `onFormChange`, `onEmployeeChange`

---

### frontend/src/components/departments/DepartmentFormModal.tsx

**Purpose**: Reusable modal for creating and editing departments.

**Why this file exists**: The departments page needs a form for department name, code, description, and active status.

**Used by**: `DepartmentsPage.tsx`

**Props**: `open`, `editing`, `form`, `submitting`, `formError`, `onClose`, `onSubmit`, `onFormChange`

---

### frontend/src/components/employees/EmployeeFormModal.tsx

**Purpose**: Reusable modal for creating and editing employees.

**Why this file exists**: The employees page needs a form for all employee fields including role, department, designation, and joining date.

**Used by**: `EmployeesPage.tsx`

**Props**: `open`, `editing`, `departments`, `designations`, `form`, `submitting`, `formError`, `onClose`, `onSubmit`, `onFormChange`

---

### frontend/src/pages/employees/EmployeesPage.tsx

**Purpose**: Employee management page with search, filters, and CRUD.

**Why this file exists**: MANAGER roles need a full interface to manage employees. Regular employees access their own profile via the auth pages.

**Used by**: `AppRoutes.tsx`

**Flow**:
```
Mount → fetch departments/designations → list employees
Create/Edit → EmployeeFormModal → dispatch create/update → refresh list
Status toggle → window.confirm → dispatch update → refresh list
```

---

### frontend/src/pages/attendance/AttendancePage.tsx

**Purpose**: Role-aware attendance page with check-in/out and management.

**Why this file exists**: Employees need quick check-in/out. Managers need to view and mark attendance for all employees.

**Used by**: `AppRoutes.tsx`

**Flow**:
```
EMPLOYEE: see today's card → Check In / Check Out → refresh list
MANAGER: select employee → filter by date/status → mark attendance → refresh
```

---

### frontend/src/pages/leaves/LeavesPage.tsx

**Purpose**: Leave management page with apply, list, and approve/reject.

**Why this file exists**: Employees apply for leave; managers approve or reject pending requests.

**Used by**: `AppRoutes.tsx`

---

### frontend/src/hooks/useAttendance.ts

**Purpose**: Custom hook exposing attendance state and actions.

**Why this file exists**: Encapsulates Redux store access for attendance so pages don't directly import store internals.

**Used by**: `AttendancePage.tsx`

**Returns**: `{ records, summary, loading, error, list, mark, update, loadSummary, checkIn, checkOut, clear }`

---

### frontend/src/hooks/useLeaves.ts

**Purpose**: Custom hook exposing leave state and actions.

**Why this file exists**: Encapsulates Redux store access for leaves.

**Used by**: `LeavesPage.tsx`

**Returns**: `{ leaves, total_records, total_pages, page, page_size, loading, error, list, apply, updateStatus, clear }`

---

### frontend/src/hooks/useDepartments.ts

**Purpose**: Custom hook exposing department state and actions.

**Why this file exists**: Encapsulates Redux store access for departments.

**Used by**: `DepartmentsPage.tsx`, `EmployeesPage.tsx`, `EmployeeFormModal.tsx`

**Returns**: `{ departments, total_records, total_pages, page, page_size, loading, error, list, create, update, clear }`

---

### frontend/src/hooks/useDesignations.ts

**Purpose**: Custom hook exposing designation state and actions.

**Why this file exists**: Encapsulates Redux store access for designations.

**Used by**: `DesignationsPage.tsx`, `EmployeesPage.tsx`, `EmployeeFormModal.tsx`

**Returns**: `{ designations, total_records, total_pages, page, page_size, loading, error, list, create, update, clear }`

---

### frontend/src/store/slices/attendanceSlice.ts

**Purpose**: Redux slice for attendance state and async thunks.

**Why this file exists**: Centralizes attendance state and API calls.

**Used by**: `useAttendance.ts`

**Thunks**: `fetchAttendance`, `markAttendance`, `updateAttendance`, `fetchAttendanceSummary`, `checkIn`, `checkOut`

**State shape**: `{ records, summary, loading, error, page, page_size, total_records, total_pages }`

---

### frontend/src/store/slices/leaveSlice.ts

**Purpose**: Redux slice for leave state and async thunks.

**Why this file exists**: Centralizes leave state and API calls.

**Used by**: `useLeaves.ts`

**Thunks**: `fetchLeaves`, `applyLeave`, `updateLeaveStatus`

**State shape**: `{ leaves, total_records, total_pages, page, page_size, loading, error }`

---

### frontend/src/store/slices/employeeSlice.ts

**Purpose**: Redux slice for employee state and async thunks.

**Why this file exists**: Centralizes employee state and API calls.

**Used by**: `useEmployees.ts`

**Thunks**: `fetchEmployees`, `createEmployee`, `updateEmployee`

**State shape**: `{ employees, total_records, total_pages, page, page_size, loading, error }`

**Note**: No delete thunk — employee deletion is not exposed in the UI.

---

### frontend/src/store/slices/designationSlice.ts

**Purpose**: Redux slice for designation state and async thunks.

**Why this file exists**: Centralizes designation state and API calls.

**Used by**: `useDesignations.ts`

**Thunks**: `fetchDesignations`, `createDesignation`, `updateDesignation`

**State shape**: `{ designations, total_records, total_pages, page, page_size, loading, error }`

---

### frontend/src/types/employee.ts

**Purpose**: TypeScript interfaces for employee data.

**Why this file exists**: Keeps frontend and backend type-compatible for employee operations.

**Used by**: `EmployeesPage.tsx`, `EmployeeFormModal.tsx`, `useEmployees.ts`, `employeeSlice.ts`

**Exports**: `Employee`, `CreateEmployeePayload`, `UpdateEmployeePayload`, `EmployeeListResponse`, `EmployeeListParams`

---

### frontend/src/types/attendance.ts

**Purpose**: TypeScript interfaces for attendance data.

**Why this file exists**: Keeps frontend and backend type-compatible for attendance operations.

**Used by**: `AttendancePage.tsx`, `AttendanceFormModal.tsx`, `useAttendance.ts`, `attendanceSlice.ts`

**Exports**: `AttendanceRecord`, `AttendanceListResponse`, `AttendanceSummary`

---

### frontend/src/types/leave.ts

**Purpose**: TypeScript interfaces for leave data.

**Why this file exists**: Keeps frontend and backend type-compatible for leave operations.

**Used by**: `LeavesPage.tsx`, `useLeaves.ts`, `leaveSlice.ts`

**Exports**: `LeaveRecord`, `LeaveListResponse`

---

### frontend/src/types/report.ts

**Purpose**: TypeScript interfaces for report data.

**Why this file exists**: Keeps frontend and backend type-compatible for report operations.

**Used by**: `ReportsPage.tsx`, `report.service.ts`

**Exports**: `ReportFilters`, `ReportSummary`, `ReportRecord`

---

### frontend/src/types/dashboard.ts

**Purpose**: TypeScript interfaces for dashboard data.

**Why this file exists**: Keeps frontend and backend type-compatible for dashboard statistics.

**Used by**: `AdminDashboardPage.tsx`, `HRDashboardPage.tsx`, `SuperAdminDashboardPage.tsx`, `EmployeeDashboardPage.tsx`, `DashboardContent.tsx`

**Exports**: `StatItem`, `ActivityItem`

---

### frontend/src/types/activityLog.ts

**Purpose**: TypeScript interfaces for activity log data.

**Why this file exists**: Keeps frontend and backend type-compatible for activity log operations.

**Used by**: `ActivityLogsPage.tsx`, `activityLogSlice.ts`

**Exports**: `ActivityLog`, `ActivityLogFilters`, `DistinctAction`

---

### frontend/src/hooks/useDepartments.ts

**Purpose**: Custom hook exposing department state and actions.

**Why this file exists**: Encapsulates Redux store access for departments.

**Used by**: `DepartmentsPage.tsx`, `EmployeesPage.tsx`, `EmployeeFormModal.tsx`

**Returns**: `{ departments, total_records, total_pages, page, page_size, loading, error, list, create, update, clear }`

---

### frontend/src/hooks/useDesignations.ts

**Purpose**: Custom hook exposing designation state and actions.

**Why this file exists**: Encapsulates Redux store access for designations.

**Used by**: `DesignationsPage.tsx`, `EmployeesPage.tsx`, `EmployeeFormModal.tsx`

**Returns**: `{ designations, total_records, total_pages, page, page_size, loading, error, list, create, update, clear }`

---

## Frontend: Payroll & Payment

### frontend/src/types/payroll.ts

**Purpose**: TypeScript interfaces for payroll data.

**Why this file exists**: Keeps frontend and backend type-compatible for payroll operations.

**Used by**: `PayrollPage.tsx`, `payrollSlice.ts`, `payroll.service.ts`, `usePayroll.ts`

**Exports**: `Payroll`, `PayrollFilters`, `PayrollListResponse`, `CreatePayrollPayload`, `UpdatePayrollPayload`

---

### frontend/src/types/payment.ts

**Purpose**: TypeScript interfaces for payment data.

**Why this file exists**: Keeps frontend and backend type-compatible for payment operations.

**Used by**: `PaymentsPage.tsx`, `paymentSlice.ts`, `payment.service.ts`, `usePayment.ts`

**Exports**: `Payment`, `PaymentFilters`, `PaymentListResponse`, `CreatePaymentPayload`, `UpdatePaymentPayload`

---

### frontend/src/services/payroll.service.ts

**Purpose**: API client for payroll endpoints.

**Why this file exists**: Centralizes all payroll API calls.

**Used by**: `usePayroll.ts`, `EmployeeDashboardPage.tsx`

**Functions**: `create`, `list`, `get`, `update`, `approve`, `cancel`, `getMyPayrolls`

---

### frontend/src/services/payment.service.ts

**Purpose**: API client for payment endpoints.

**Why this file exists**: Centralizes all payment API calls.

**Used by**: `usePayment.ts`, `EmployeeDashboardPage.tsx`

**Functions**: `create`, `list`, `get`, `update`, `getMyPayments`

---

### frontend/src/store/slices/payrollSlice.ts

**Purpose**: Redux slice for payroll state and async thunks.

**Why this file exists**: Centralizes payroll state and API calls.

**Used by**: `usePayroll.ts`

**Thunks**: `fetchPayrolls`, `createPayroll`, `updatePayroll`, `approvePayroll`, `cancelPayroll`, `fetchMyPayrolls`

**State shape**: `{ payrolls, total_records, total_pages, page, page_size, loading, error }`

---

### frontend/src/store/slices/paymentSlice.ts

**Purpose**: Redux slice for payment state and async thunks.

**Why this file exists**: Centralizes payment state and API calls.

**Used by**: `usePayment.ts`

**Thunks**: `fetchPayments`, `createPayment`, `updatePayment`, `fetchMyPayments`

**State shape**: `{ payments, total_records, total_pages, page, page_size, loading, error }`

---

### frontend/src/hooks/usePayroll.ts

**Purpose**: Custom hook exposing payroll state and actions.

**Why this file exists**: Encapsulates Redux store access for payroll.

**Used by**: `PayrollPage.tsx`

**Returns**: `{ payrolls, total_records, total_pages, page, page_size, loading, error, list, create, update, approve, cancel, loadMyPayrolls, clear }`

---

### frontend/src/hooks/usePayment.ts

**Purpose**: Custom hook exposing payment state and actions.

**Why this file exists**: Encapsulates Redux store access for payment.

**Used by**: `PaymentsPage.tsx`

**Returns**: `{ payments, total_records, total_pages, page, page_size, loading, error, list, create, update, loadMyPayments, clear }`

---

### frontend/src/pages/payroll/PayrollPage.tsx

**Purpose**: Role-aware payroll management page.

**Why this file exists**: Managers need to generate, view, approve, and cancel payrolls. Employees view their own payrolls.

**Used by**: `AppRoutes.tsx`

**Flow**:
```
Mount → fetch payrolls based on role
Manager: Create Payroll → Modal → dispatch create → refresh list
Manager: Approve/Cancel → confirm → dispatch approve/cancel → refresh list
Employee: read-only table of own payrolls
```

---

### frontend/src/pages/payments/PaymentsPage.tsx

**Purpose**: Role-aware payment management page.

**Why this file exists**: Managers need to record payments, view all, and update status. Employees view their own payment history.

**Used by**: `AppRoutes.tsx`

**Flow**:
```
Mount → fetch payments based on role
Manager: Record Payment → Modal → dispatch create → refresh list
Manager: Update Status → dropdown → dispatch update → refresh list
Employee: read-only table of own payments
```

---

### frontend/src/utils/constants.ts (updated)

**Purpose**: Added payroll and payment routes and nav items.

**Changes**:
- Added `ROUTES.PAYROLL = "/payroll"` and `ROUTES.PAYMENTS = "/payments"`
- Added `baseNav.payments` with icon and route
- Added `payments` to `SUPER_ADMIN_NAV`, `ADMIN_NAV`, `HR_NAV`, and `EMPLOYEE_NAV`
- Changed `baseNav.payroll.to` from `PLACEHOLDER_ROUTE` to `ROUTES.PAYROLL`
- Added `baseNav.payroll` to `HR_NAV`

---

## Data Flow Diagrams

### Backend: Request Lifecycle

```
1. Django URL router matches path to URLConf
2. Middleware processes request (CORS, auth, logging, exceptions)
3. Controller (APIView) receives request
4. Serializer validates request data
5. Service executes business logic
6. Repository performs MongoDB operation
7. Service returns result to controller
8. Controller wraps result in ApiResponse
9. Response returned to frontend
```

### Frontend: Data Flow

```
1. Page component mounts
2. Custom hook dispatches Redux thunk
3. Thunk calls service function
4. Service uses Axios instance to call backend
5. Axios interceptor attaches auth token
6. Backend processes request and returns JSON
7. Thunk stores result in Redux slice
8. Page re-renders with new data
```
