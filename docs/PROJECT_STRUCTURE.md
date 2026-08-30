# Project Structure

This document explains every important folder in the EmpSphere monorepo. It is designed for developers who want to understand where code lives and why.

---

## Monorepo Root

```
EmpSphere/
├── backend/                 # Django REST API server
├── frontend/                # React + Vite web application
├── docs/                    # Project documentation
├── .gitignore               # Git ignore rules
├── .github/                 # GitHub Actions workflows
├── .kilo/                   # Kilo configuration
├── .vscode/                 # VS Code workspace settings
├── node_modules/            # Frontend dependencies (gitignored)
├── package.json             # Frontend scripts and dependencies
└── package-lock.json        # Locked dependency versions
```

**Why it exists**: EmpSphere is a monorepo — a single repository containing both the backend API and the frontend web app. This keeps the full-stack codebase in one place.

**What belongs here**: Root-level configuration only (`package.json`, `.gitignore`, `.github/`).

**What should NOT be placed here**: Application source code, build artifacts, or environment files.

---

## Backend

```
backend/
├── manage.py                        # Django CLI entry point
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (gitignored)
├── config/                           # Django project configuration
│   ├── __init__.py
│   ├── settings.py                   # Main Django settings
│   ├── urls.py                       # Root URL router
│   ├── wsgi.py                       # WSGI deployment config
│   └── asgi.py                       # ASGI deployment config
├── apps/                             # All Django applications
│   ├── common/                       # Shared utilities
│   ├── authentication/               # Auth flows
│   ├── organization/                 # Departments & designations
│   ├── employee/                     # Employee management
│   ├── attendance/                   # Attendance & check-in/out
│   ├── leave/                        # Leave management
│   ├── payment/                      # Office payment processing with Cashfree
│   ├── activity_logs/                # Activity logging
│   ├── statistics/                   # Dashboard statistics
│   └── reports/                      # Report generation
├── templates/
│   └── emails/
│       └── otp_email.html            # OTP email template
└── logs/
    └── app.log                       # Application logs (gitignored)
```

### config/

**Why it exists**: Django requires a project-level configuration package. `config/` holds the global settings, URL routing, and deployment entry points.

**What belongs here**:
- `settings.py` — Installed apps, middleware, DRF config, JWT, CORS, email, logging
- `urls.py` — Top-level URL patterns mounting each app
- `wsgi.py` / `asgi.py` — Deployment entry points

**What should NOT be placed here**: Business logic, serializers, or database queries. Those belong in `apps/`.

**Interacts with**: Every file in `apps/` imports from `config/settings.py`.

**Example** (`settings.py:54-63`):
```python
INSTALLED_APPS = [
    "rest_framework",
    "corsheaders",
    "apps.authentication",
    "apps.organization",
    "apps.employee",
    "apps.attendance",
    "apps.leave",
    "apps.activity_logs",
    "apps.statistics",
    "apps.common",
    "apps.reports",
]
```

---

### apps/

**Why it exists**: Django's app registry. Each feature lives in its own isolated app with its own controllers, services, repositories, serializers, and URLs.

**What belongs here**: All feature-specific code.

**What should NOT be placed here**: Cross-cutting concerns (those belong in `apps/common/`).

**Interacts with**: `config/settings.py` (app registration), `config/urls.py` (URL mounting).

---

### apps/common/

**Why it exists**: Eliminates duplication by providing shared utilities, base classes, security helpers, and middleware used by every other app.

**What belongs here**: Code that is genuinely reused across multiple apps.

**What should NOT be placed here**: Feature-specific business logic.

**Interacts with**: Every other app in `apps/`.

**Subfolders**:

#### apps/common/base/

Base classes that other controllers, services, and managers inherit from.

| File | Purpose |
|------|---------|
| `base_controller.py` | `BaseController` — provides `success()` and `error()` response helpers |
| `base_service.py` | `BaseService` — provides `log_activity()` for audit logging |
| `base_manager.py` | `BaseManager` — empty base for data-access managers |

**Example** (`base_service.py:22-44`):
```python
class BaseService:
    def __init__(self):
        self.audit_service = AuditService()

    def log_activity(self, module, action, performed_by, target_id, status, description, metadata=None):
        self.audit_service.log(
            module=module,
            action=action,
            performed_by=performed_by,
            target_id=target_id,
            status=status,
            description=description,
            metadata=metadata or {},
        )
```

#### apps/common/config/

Application settings loaded from `.env`.

| File | Purpose |
|------|---------|
| `settings.py` | `Settings` dataclass — reads all env vars, exposes them as `settings` |

#### apps/common/core/

Constants, enums, and regex patterns used everywhere.

| File | Purpose |
|------|---------|
| `collections.py` | `Collections` — MongoDB collection name constants |
| `messages.py` | `Messages` — standardized user-facing message strings |
| `otp.py` | `OTPPurpose` — OTP type enum, `OTP_LENGTH`, `OTP_EXPIRY_MINUTES` |
| `permissions.py` | Permission constants and `ROLE_PERMISSIONS` mapping |
| `regex.py` | `PASSWORD_REGEX`, `EMAIL_REGEX` |
| `roles.py` | `Role` IntEnum, `ROLE_NAMES`, `EMPLOYEE_MANAGER_ROLES` |
| `status.py` | `StatusCode` — HTTP status code constants |

#### apps/common/database/

MongoDB connection management.

| File | Purpose |
|------|---------|
| `mongo.py` | `MongoConnection` singleton — provides `mongo.get_collection(name)` |

#### apps/common/decorators/

Reusable view decorators.

| File | Purpose |
|------|---------|
| `permission.py` | `@require_role(*allowed_roles)` — restricts APIView methods by role |

#### apps/common/exceptions/

Custom exception hierarchy and global exception handler.

| File | Purpose |
|------|---------|
| `custom_exception.py` | `CustomException`, `ValidationException`, `UnauthorizedException`, `ForbiddenException`, `NotFoundException`, `ConflictException`, `InternalServerException` |
| `exception_handler.py` | `custom_exception_handler` — DRF exception handler registered in settings |

#### apps/common/management/

Django management commands.

| File | Purpose |
|------|---------|
| `commands/seed_rbac.py` | Seeds roles, permissions, and a default Super Admin user |

#### apps/common/middleware/

Django middleware classes.

| File | Purpose |
|------|---------|
| `authentication.py` | `JWTAuthentication` — DRF auth class that validates Bearer JWT |
| `exception_middleware.py` | `ExceptionMiddleware` — catches unhandled exceptions, returns JSON |
| `request_logger.py` | `RequestLoggerMiddleware` — logs method, path, status, duration |

#### apps/common/permissions/

Role-based permission helpers.

| File | Purpose |
|------|---------|
| `role_permission.py` | `RolePermission` — `has_privilege()`, `can_manage_user()`, `owns_resource()` |

#### apps/common/responses/

Standardized API response builders.

| File | Purpose |
|------|---------|
| `api_response.py` | `ApiResponse` — `success()`, `error()`, `paginated()` |

#### apps/common/security/

Password hashing and Google OAuth helpers.

| File | Purpose |
|------|---------|
| `password_manager.py` | `PasswordManager` — bcrypt hash/verify with 72-byte limit |
| `google_manager.py` | `GoogleManager` — verifies Google ID tokens, extracts user info |

---

### apps/authentication/

**Why it exists**: All authentication and user account flows — registration, login, logout, email verification, OTP, password reset, Google login, and profile management.

**What belongs here**: Views, serializers, services, repositories, managers, and URLs for auth-related endpoints.

**What should NOT be placed here**: Employee CRUD, attendance, leave, department logic.

**Interacts with**: `apps/common/` (security, base classes), `apps/employee/` (employee code generation).

**Subfolders**:

| Folder | Purpose |
|--------|---------|
| `views/` | `APIView` classes — one per endpoint group |
| `serializers/` | DRF serializers for request validation and response shaping |
| `services/` | Business logic for auth flows |
| `repositories/` | MongoDB queries for users and OTPs |
| `managers/` | Token generation/blacklisting, employee code generation |
| `schemas/` | Direct MongoDB schema classes (bypasses DRF for raw queries) |

**Example URL mapping** (`urls.py:17-41`):
```python
urlpatterns = [
    path("register/", AuthView.as_view(), name="register"),
    path("login/", AuthView.as_view(), name="login"),
    path("logout/", AuthView.as_view(), name="logout"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("me/", UserView.as_view(), name="me"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("profile/", UserView.as_view(), name="profile"),
    path("profile/image/", ProfileImageView.as_view(), name="profile-image"),
    path("send-otp/", OTPView.as_view(), name="send-otp"),
    path("verify-otp/", OTPView.as_view(), name="verify-otp"),
    path("change-password/", PasswordView.as_view(), name="change-password"),
    path("set-password/", PasswordView.as_view(), name="set-password"),
    path("forgot-password/", PasswordView.as_view(), name="forgot-password"),
    path("reset-password/", PasswordView.as_view(), name="reset-password"),
]
```

---

### apps/organization/

**Why it exists**: Manages departments and designations — the organizational structure that employees belong to.

**What belongs here**: Department and designation CRUD endpoints, validation, and database access.

**What should NOT be placed here**: Employee records, attendance, or leave logic.

**Interacts with**: `apps/employee/` (employees reference departments and designations).

---

### apps/employee/

**Why it exists**: Employee management — creating, reading, updating, and soft-deleting employee records.

**What belongs here**: Employee CRUD endpoints, validation, and database access.

**What should NOT be placed here**: Authentication logic (users are created in `authentication`, managed as employees here).

**Interacts with**: `apps/authentication/` (reuses `UserRepository` for database operations), `apps/organization/` (departments and designations).

---

### apps/attendance/

**Why it exists**: Attendance tracking — marking attendance, check-in/check-out, and attendance summaries.

**What belongs here**: Attendance CRUD, check-in/out actions, validation, and database access.

**What should NOT be placed here**: Leave logic or employee management.

**Interacts with**: `apps/authentication/` (validates employee exists and is active).

---

### apps/leave/

**Why it exists**: Leave management — applying for leave, approving/rejecting leave requests.

**What belongs here**: Leave CRUD, approval workflow, validation, and database access.

**What should NOT be placed here**: Attendance or employee management.

**Interacts with**: `apps/authentication/` (validates employee exists and is active).

---

### apps/activity_logs/

**Why it exists**: Provides endpoints for retrieving activity log records with role-based filtering.

**What belongs here**: Activity log retrieval endpoints and distinct action listing.

**What should NOT be placed here**: Writing activity logs (that's done via `BaseService.log_activity()` in services).

**Interacts with**: `apps/common/` (base controller, permissions).

---

### apps/statistics/

**Why it exists**: Aggregates dashboard statistics from multiple collections.

**What belongs here**: Simple count aggregations for the dashboard.

**What should NOT be placed here**: Complex report generation (that belongs in `apps/reports/`).

**Interacts with**: `apps/common/` (base controller, permissions).

---

### apps/reports/

**Why it exists**: Generates structured reports (employee, attendance, leave, department, designation, activity) with summaries and paginated records.

**What belongs here**: Report orchestration, aggregation pipelines, and report endpoints.

**What should NOT be placed here**: Raw CRUD operations (those belong in their respective apps).

**Interacts with**: `apps/employee/`, `apps/attendance/`, `apps/leave/`, `apps/organization/` (reuses their services).

---

## Frontend

```
frontend/
├── .env                        # Frontend environment variables
├── index.html                  # Vite entry HTML
├── package.json                # Dependencies and scripts
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── dist/                       # Build output (gitignored)
└── src/
    ├── main.tsx                # React entry point
    ├── App.tsx                 # Root component (Redux, Router, Toast)
    ├── vite-env.d.ts           # Vite type declarations
    ├── config/
    │   ├── axios.ts            # Configured Axios instance with interceptors
    │   └── env.ts              # Environment variable access
    ├── routes/
    │   ├── AppRoutes.tsx       # Central route definitions
    │   ├── ProtectedRoute.tsx  # Auth guard
    │   ├── RequireRole.tsx     # Role guard
    │   └── DashboardRedirect.tsx # Redirects /dashboard to role-specific page
    ├── store/
    │   ├── index.ts            # Redux store configuration
    │   ├── middleware/
    │   │   └── authMiddleware.ts # Listens for logout to clear tokens
    │   └── slices/
    │       ├── authSlice.ts       # Login, register, fetchMe, logout, googleLogin
    │       ├── employeeSlice.ts   # Employee CRUD thunks
    │       ├── departmentSlice.ts # Department CRUD thunks
    │       ├── designationSlice.ts # Designation CRUD thunks
    │       ├── attendanceSlice.ts # Attendance thunks
    │       ├── leaveSlice.ts      # Leave thunks
    │       └── paymentSlice.ts    # Office payment thunks
    ├── hooks/
    │   ├── useAuth.ts          # Auth selectors and actions
    │   ├── useEmployees.ts     # Employee selectors and actions
    │   ├── useDepartments.ts   # Department selectors and actions
    │   ├── useDesignations.ts  # Designation selectors and actions
    │   ├── useAttendance.ts    # Attendance selectors and actions
    │   ├── useLeaves.ts        # Leave selectors and actions
    │   ├── usePayment.ts       # Office payment selectors and actions
    │   └── useDashboardData.ts # Dashboard data loading
    ├── services/
    │   ├── api.ts              # Generic HTTP wrapper (get/post/put/patch/delete)
    │   ├── auth.service.ts      # Auth API endpoints
    │   ├── user.service.ts      # User/profile API endpoints
    │   ├── employee.service.ts  # Employee API endpoints
    │   ├── department.service.ts # Department API endpoints
    │   ├── designation.service.ts # Designation API endpoints
    │   ├── attendance.service.ts # Attendance API endpoints
    │   ├── leave.service.ts     # Leave API endpoints
    │   ├── payment.service.ts   # Office payment API endpoints
    │   ├── activityLog.service.ts # Activity log API endpoints
    │   ├── report.service.ts    # Report API endpoints
    │   └── statistics.service.ts # Statistics API endpoints
    ├── components/
    │   ├── AppBootstrap.tsx     # Session restoration on app load
    │   ├── common/              # Reusable UI primitives
    │   │   ├── Avatar.tsx       # Profile image with initials fallback
    │   │   ├── Button.tsx       # Button with variants and loading state
    │   │   ├── Input.tsx        # Labeled input with error/hint
    │   │   ├── Loader.tsx       # Centered spinner
    │   │   ├── Modal.tsx        # Accessible dialog
    │   │   ├── PageHeader.tsx   # Title + subtitle + actions
    │   │   ├── Pagination.tsx   # Previous/Next page controls
    │   │   ├── StatusBadge.tsx  # Color-coded status indicator
    │   │   └── ToastProvider.tsx # Toast notifications
    │   ├── layout/              # App shell
    │   │   ├── DashboardLayout.tsx # Sidebar + Navbar + content
    │   │   ├── Navbar.tsx       # Top bar with user dropdown
    │   │   └── Sidebar.tsx      # Role-aware navigation
    │   ├── dashboard/
    │   │   └── DashboardContent.tsx # Shared dashboard shell
    │   ├── auth/                # Auth form components
    │   │   ├── AuthPageShell.tsx     # Centered auth card
    │   │   ├── LoginForm.tsx         # Email/password + Google login
    │   │   ├── RegisterForm.tsx      # Registration with company secret
    │   │   ├── ForgotPasswordForm.tsx # Step 1: request OTP
    │   │   ├── ResetPasswordForm.tsx  # Steps 2-3: verify OTP + reset
    │   │   ├── VerifyEmailForm.tsx    # OTP send + verify
    │   │   ├── ChangePasswordForm.tsx # Current + new password
    │   │   ├── SetPasswordForm.tsx    # Two-step for Google users
    │   │   └── GoogleAuthButton.tsx   # Google Identity Services
    │   ├── attendance/
    │   │   └── AttendanceFormModal.tsx # Attendance create/edit modal
    │   ├── departments/
    │   │   └── DepartmentFormModal.tsx # Department create/edit modal
    │   ├── designations/
    │   │   └── DesignationFormModal.tsx # Designation create/edit modal (UNUSED)
    │   └── employees/
    │       └── EmployeeFormModal.tsx   # Employee create/edit modal
    ├── pages/
    │   ├── dashboard/           # Role-specific dashboards
    │   ├── employees/           # Employee list and detail
    │   ├── departments/         # Department list and detail
    │   ├── designations/        # Designation list
    │   ├── attendance/          # Attendance management
    │   ├── leaves/              # Leave management
    │   ├── payments/            # Office payment management
    │   ├── profile/             # Profile view/edit + image upload
    │   ├── activityLogs/        # Activity log viewer
    │   ├── reports/             # Report generation
    │   ├── auth/                # Auth pages (thin wrappers)
    │   └── errors/              # 404 and 403 pages
    ├── types/                   # TypeScript interfaces
    │   ├── api.ts               # ApiResponse, ApiErrorResponse
    │   ├── auth.ts              # User, LoginResult, payloads
    │   ├── employee.ts          # Employee types
    │   ├── department.ts        # Department types
    │   ├── designation.ts       # Designation types
    │   ├── attendance.ts        # Attendance types
    │   ├── leave.ts             # Leave types
    │   ├── payment.ts           # Office payment types
    │   ├── activityLog.ts       # Activity log types
    │   ├── report.ts            # Report types
    │   └── dashboard.ts         # StatItem, ActivityItem
    ├── utils/
    │   ├── helpers.ts           # cn, formatDate, getErrorMessage, getProfileImageUrl
    │   ├── constants.ts         # ROLES, ROUTES, nav items
    │   ├── token.ts             # localStorage token wrapper
    │   └── exportCsv.ts         # CSV export utility
    └── styles/
        └── globals.css          # Tailwind + component CSS classes
```

### src/config/

**Why it exists**: Centralizes HTTP client configuration and environment variable access.

**What belongs here**: Axios instance setup, interceptors, and env var definitions.

**Interacts with**: All `services/` files, `AppBootstrap.tsx`, `AuthPageShell.tsx`.

---

### src/store/

**Why it exists**: Redux Toolkit store with slices for each domain entity and auth middleware.

**What belongs here**: Slice reducers, thunks, and middleware.

**Interacts with**: All `hooks/`, all `services/`, `App.tsx`, `AppBootstrap.tsx`.

---

### src/hooks/

**Why it exists**: Encapsulates Redux selectors and action dispatchers so pages don't directly import store internals.

**What belongs here**: One hook per domain entity, exposing state and actions.

**Interacts with**: `src/store/slices/`, `src/pages/`.

---

### src/services/

**Why it exists**: All API communication lives here. Pages and hooks call services; services call the backend.

**What belongs here**: One service file per API domain, using the shared `api` Axios instance.

**Interacts with**: `src/config/axios.ts`, `src/store/slices/`, `src/pages/`.

---

### src/components/

**Why it exists**: Reusable UI components. Shared across pages and organized by feature.

**What belongs here**: Pure UI components with minimal business logic.

**What should NOT be placed here**: Page-level routing or data fetching (those belong in `pages/` and `hooks/`).

**Interacts with**: `src/pages/`, `src/hooks/`, `src/utils/`.

---

### src/pages/

**Why it exists**: Page-level components that compose hooks, services, and shared components into full screens.

**What belongs here**: Route-level components, data fetching, and page-specific state.

**What should NOT be placed here**: Reusable UI primitives (those belong in `components/`).

**Interacts with**: `src/hooks/`, `src/services/`, `src/components/`.

---

### src/types/

**Why it exists**: Centralized TypeScript interfaces so the frontend and backend stay type-compatible.

**What belongs here**: exported interfaces and types for API payloads and responses.

**Interacts with**: `src/services/`, `src/store/slices/`, `src/components/`, `src/pages/`.

---

### src/utils/

**Why it exists**: Pure helper functions with no framework dependencies.

**What belongs here**: Formatting, validation, token storage, CSV export.

**Interacts with**: Everywhere.
