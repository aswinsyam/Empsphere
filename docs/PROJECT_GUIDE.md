# EmpSphere — Complete Project Guide

A beginner-friendly guide to understanding the EmpSphere Employee Management System.

---

## Table of Contents

1. [What is EmpSphere?](#1-what-is-empsphere)
2. [Technology Stack](#2-technology-stack)
3. [Current Project Structure](#3-current-project-structure)
4. [Backend Architecture](#4-backend-architecture)
5. [Frontend Architecture](#5-frontend-architecture)
6. [How a Request Travels Through the System](#6-how-a-request-travels-through-the-system)
7. [Authentication](#7-authentication)
8. [JWT Authentication](#8-jwt-authentication)
9. [Authorization and Roles](#9-authorization-and-10-roles)
10. [Permission Decorator](#10-permission-decorator)
11. [Employee Management](#11-employee-management)
12. [Employee Creation — Complete Flow](#12-employee-creation--complete-flow)
13. [Departments](#13-departments)
14. [Designations](#14-designations)
15. [Attendance](#15-attendance)
16. [Leave Management](#16-leave-management)
17. [Profile and Image Upload](#17-profile-and-image-upload)
18. [Payment System](#18-payment-system)
19. [Activity Logs](#19-activity-logs)
20. [Reports](#20-reports)
21. [Statistics and Dashboards](#21-statistics-and-dashboards)
22. [MongoDB](#22-mongodb)
23. [Axios and API Communication](#23-axios-and-api-communication)
24. [Environment Variables](#24-environment-variables)
25. [Running the Project](#25-running-the-project)
26. [Verification](#26-verification)
27. [Debugging Guide](#27-debugging-guide)
28. [Deployment](#28-deployment)
29. [Safe Development Rules](#29-safe-development-rules)
30. [Fresher Learning Path](#30-fresher-learning-path)
31. [Quick File Reference](#31-quick-file-reference)
32. [How EmpSphere Works — Final Summary](#32-how-empsphere-works--final-summary)

---

## 1. What is EmpSphere?

EmpSphere is a **full-stack Employee Management System** that helps a company manage:

- Employee records (create, list, update, delete)
- Departments and designations
- Attendance (check-in / check-out)
- Leave applications and approvals
- Office amenity payments via **Razorpay (Test Mode)**
- Activity logging (audit trail)
- Dashboard statistics and reports

The system uses **role-based access control (RBAC)** so a Super Admin, Admin, HR Manager, and Employee each see only what they are allowed to see.

---

## 2. Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend framework | Django 4.2 + DRF | HTTP API, request handling |
| Backend language | Python 3.8+ | Business logic |
| Database driver | PyMongo 4.10 | Talk to MongoDB |
| Auth | PyJWT 2.9 | Issue and verify access / refresh tokens |
| Password hashing | passlib + bcrypt | Secure password storage |
| Config | python-dotenv | Load secrets from `.env` |
| Frontend | React 18 + TypeScript | UI |
| Build tool | Vite 5 | Fast dev server and production build |
| State (auth) | Redux Toolkit | Holds logged-in user globally |
| Routing | React Router v7 | Page navigation |
| HTTP client | Axios | API calls + JWT refresh interceptor |
| Styling | Tailwind CSS | Utility-first CSS |
| Database | MongoDB | Primary data store |
| Payments | Razorpay (Test Mode) | Office amenity payments |

> **Note:** The `DATABASES` setting in `config/settings.py` points to an in-memory SQLite database (`:memory:`). This is only used by Django itself for internal tables. All real data is in **MongoDB**.

---

## 3. Current Project Structure

```
EmpSphere/
├── backend/
│   ├── config/                 # Django project (settings, urls, wsgi/asgi)
│   ├── apps/
│   │   ├── authentication/     # register / login / JWT / OTP / password / Google
│   │   ├── common/             # shared utilities (auth, permissions, db, settings, constants)
│   │   ├── employees/          # Employee CRUD
│   │   ├── departments/        # Department CRUD
│   │   ├── designations/       # Designation CRUD
│   │   ├── attendance/         # Check-in / check-out
│   │   ├── leaves/             # Apply / approve leave
│   │   ├── payments/           # Razorpay payments + amenities
│   │   ├── activity_logs/      # Audit log read endpoint
│   │   ├── reports/            # Management reports
│   │   └── statistics/         # Dashboard counts
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── frontend/                   # React + TypeScript SPA
│   └── src/
│       ├── components/         # UI components (auth, layout, common, dashboard, ...)
│       ├── pages/              # Page-level components (one folder per feature)
│       ├── routes/             # AppRoutes, ProtectedRoute, RequireRole, DashboardRedirect
│       ├── services/           # One file per feature, calls Axios
│       ├── hooks/              # useAuth, useResource, useDashboardData
│       ├── store/              # Redux store (only auth slice)
│       ├── types/              # TypeScript types
│       ├── utils/              # token storage, helpers, csv export, constants
│       └── config/             # axios + env
├── docs/                       # this file
├── .github/workflows/          # CI
├── README.md
└── .gitignore
```

Each backend app follows the same simple shape:

```
<app>/
├── views.py          # HTTP endpoints (DRF APIView)
├── services.py       # Business logic
├── serializers.py    # Request validation
├── urls.py           # URL routes for this app
└── apps.py           # Django app config
```

There is **no** `controllers/`, `repositories/`, `dtos/`, `validators/`, `managers/`, or `schemas/` layer. Services talk to MongoDB directly through `get_collection(...)`. This keeps the code short and easy to follow.

---

## 4. Backend Architecture

The whole backend follows one simple flow:

```
HTTP Request
   ↓
URL  (config/urls.py → apps/<app>/urls.py)
   ↓
View (apps/<app>/views.py)
   ↓ validates with a DRF serializer
Service (apps/<app>/services.py)
   ↓ talks to MongoDB
get_collection("...")
   ↓
MongoDB
```

### Example: Creating an employee

```text
POST /api/employees/
   ↓
config/urls.py → apps/employees/urls.py
   ↓
EmployeeView.post()                                 apps/employees/views.py
   ↓   @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
   ↓   EmployeeSerializer.is_valid(...)
   ↓
EmployeeService.create_employee(data)               apps/employees/services.py
   ↓   hash password, validate email/role/status
   ↓   audit log
   ↓
get_collection("users").insert_one(...)
   ↓
MongoDB "users" collection
   ↓
Response: { "user_id": "<new employee ObjectId>" }
```

### Why a service layer?

- The view is small and only deals with HTTP (request, validation, response).
- The service contains the **business rules** (who can do what, what email is valid, what role is allowed).
- The data access is **direct** — there is no repository wrapper. PyMongo is already a thin, friendly API.

### The common app

The `common` app holds shared utilities used by every other app:

| File | Purpose |
|------|---------|
| `apps/common/authentication.py` | `JWTAuthentication` DRF class |
| `apps/common/permissions.py` | `require_role` decorator + `IsAuthenticatedUser` + `can_manage_user` |
| `apps/common/database.py` | MongoDB connection (`mongo`, `get_collection`) |
| `apps/common/settings.py` | Single `settings` object loaded from `.env` |
| `apps/common/constants.py` | Collection names, OTP policy, password rules, roles |
| `apps/common/utils.py` | Password hashing, employee code generation, user lookups |
| `apps/common/responses.py` | `success()` and `error()` response helpers |
| `apps/common/exception_middleware.py` | Safety net for unhandled exceptions |
| `apps/common/request_logger.py` | Logs each request with method, path, status, duration |

---

## 5. Frontend Architecture

```
User action
   ↓
React component
   ↓ (calls a hook or directly calls a service)
Hook (e.g. useAuth, useResource)         ← optional, for stateful features
   ↓
Service (e.g. employee.service.ts)
   ↓
http wrapper (unwraps {success, message, data})
   ↓
Axios instance (with JWT interceptor)
   ↓
Backend API
   ↓
Response flows back: update state, re-render
```

- **Axios instance** — one instance in `src/config/axios.ts` with:
  - `baseURL` from `VITE_API_BASE_URL`
  - attaches the access token to every non-public request
  - on 401, tries to refresh the token once and retries the original request
- **http wrapper** — `src/services/api.ts` unwraps the backend's `{success, message, data}` envelope automatically via `unwrap()`.
- **Services** — one file per feature (`auth.service.ts`, `employee.service.ts`, etc.) using the `http` wrapper.
- **Hooks** — `useAuth` (Redux auth state), `useResource` (list/update pattern), `useDashboardData` (stats + activities).
- **Redux** — only for the **auth** slice. Everything else is component-local state.
- **Routing** — `AppRoutes` declares public + protected routes. `ProtectedRoute` redirects unauthenticated users to `/login`. `RequireRole` redirects users without the right role to their own dashboard.

---

## 6. How a Request Travels Through the System

```text
User clicks "Create Employee"
       ↓
EmployeesPage (React component)
       ↓
employeeService.create(payload)           ← calls http.post()
       ↓
http.post() unwraps the response envelope ← services/api.ts
       ↓
Axios interceptor attaches JWT             ← config/axios.ts
       ↓
POST /api/employees/                      ← Authorization: Bearer <token>
       ↓
config/urls.py → apps/employees/urls.py
       ↓
EmployeeView.post()                       ← apps/employees/views.py
       ↓ @require_role checks JWT role
       ↓ EmployeeSerializer validates input
       ↓
EmployeeService.create_employee(data)     ← apps/employees/services.py
       ↓ hash_password(), generate_employee_code()
       ↓ log_activity()
       ↓
get_collection("users").insert_one(...)
       ↓
MongoDB
       ↓
Response: { success, message, data: { user_id } }
       ↓
Frontend unwraps data, updates UI
```

---

## 7. Authentication

### Token types

- **Access token** — short-lived (default 30 minutes), sent on every protected API call.
- **Refresh token** — longer-lived (default 7 days), used only to mint a new access token when the current one expires.

Both are signed with `JWT_SECRET` from `.env`.

### Flow: Login

```text
POST /api/auth/login/   { email, password }
   ↓
AuthService.login()
   ↓ check user by email
   ↓ verify password (bcrypt via passlib)
   ↓
   ↓ if email not verified → return { requires_otp: true, email }
   ↓ else                  → create access + refresh tokens, return both
```

### Flow: Register

```text
POST /api/auth/register/   { first_name, last_name, email, password, company_secret }
   ↓
AuthService.register()
   ↓ validate company_secret
   ↓ hash password, generate employee code
   ↓ create user with role = "ADMIN"
   ↓ send email verification OTP
   ↓
MongoDB "users" collection
```

### Flow: Email verification (first login OTP)

```text
POST /api/auth/verify-otp/   { email, otp, purpose: "email_verification" }
   ↓
AuthService.verify_first_login()
   ↓ verify OTP
   ↓ mark user is_email_verified = true
   ↓ issue access + refresh tokens
```

### Flow: Forgot password

```text
POST /api/auth/forgot-password/   { email }
   ↓
PasswordService.request_password_reset()
   ↓ send forgot_password OTP
   ↓
POST /api/auth/verify-otp/   { email, otp, purpose: "forgot_password" }
   ↓
PasswordService.verify_password_reset_otp()
   ↓ verify OTP
   ↓ return single-use reset_token
   ↓
POST /api/auth/reset-password/   { reset_token, password }
   ↓
PasswordService.reset_password()
   ↓ verify reset_token
   ↓ hash new password, invalidate token
   ↓ blacklist all user sessions
```

### Flow: Change password

```text
POST /api/auth/change-password/   { current_password, new_password }
   ↓
PasswordService.change_password()
   ↓ verify current password
   ↓ hash new password
```

### Flow: Set password (Google users)

```text
POST /api/auth/set-password/   { email, otp, new_password }
   ↓
OTPService.verify_otp() + PasswordService.set_password()
```

### Flow: Google login

```text
POST /api/auth/google-login/   { id_token }
   ↓
AuthService.google_login()
   ↓ verify Google ID token
   ↓ find or link user by google_id / email
   ↓ issue tokens
```

### Flow: Logout

```text
POST /api/auth/logout/   { refresh_token }
   ↓
blacklist_token(refresh_token)
   ↓ store in MongoDB "tokens" collection
   ↓ audit log
```

### Files

| File | Purpose |
|------|---------|
| `apps/authentication/views.py` | All auth views (Register, Login, Logout, Refresh, Profile, OTP, Password, Google) |
| `apps/authentication/services.py` | AuthService, OTPService, PasswordService, UserService, ProfileImageService + token helpers |
| `apps/authentication/serializers.py` | All auth serializers |
| `apps/authentication/urls.py` | Auth URL routes |
| `apps/common/authentication.py` | `JWTAuthentication` DRF class |
| `apps/common/utils.py` | `hash_password`, `verify_password`, `generate_employee_code` |

---

## 8. JWT Authentication

### Token creation

Tokens are created in `apps/authentication/services.py`:

- `_generate_access_token(user)` — contains `user_id`, `email`, `role`, `token_type: "access"`.
- `_generate_refresh_token(user)` — same fields plus `token_type: "refresh"` and a unique `jti`.

### Token validation

`apps/common/authentication.py` — `JWTAuthentication.authenticate()`:

1. Read `Authorization: Bearer <token>` from the request.
2. Decode and validate the JWT (signature + expiry).
3. Check `token_type == "access"`.
4. Load the user from MongoDB by `user_id`.
5. Attach `(user_document, token)` to `request.user`.

### Token refresh

`apps/authentication/services.py` — `AuthService.refresh_access_token()`:

1. Check the refresh token is not blacklisted.
2. Decode and validate it.
3. Blacklist the old refresh token (rotation).
4. Issue new access + refresh tokens.

### Token blacklist

`apps/authentication/services.py`:

- `blacklist_token(refresh_token)` — stores the token in MongoDB `tokens` collection.
- `is_token_blacklisted(refresh_token)` — checks if token is blacklisted.

### Flow: Protected request

```text
GET /api/employees/  Authorization: Bearer <access_token>
   ↓
JWTAuthentication (apps/common/authentication.py)
   ↓ decode token, check token_type == "access"
   ↓ load user from MongoDB by user_id
   ↓ set request.user = user document
   ↓
@require_role checks role
   ↓
View runs
```

### Flow: Token refresh (in the Axios interceptor)

```text
Request → 401 Unauthorized
   ↓
Axios response interceptor (config/axios.ts)
   ↓ POST /auth/refresh-token/ with { refresh_token }
   ↓
   ↓ on success: save new tokens, retry the original request once
   ↓ on failure: clear tokens, dispatch auth:expired → redirect to /login
```

---

## 9. Authorization and Roles

Four roles:

| Role | Level | Description |
|------|-------|-------------|
| `SUPER_ADMIN` | 4 | Full system access |
| `ADMIN` | 3 | Manage HR managers and employees |
| `HR_MANAGER` | 2 | Manage employees |
| `EMPLOYEE` | 1 | Own data only |

### Two ideas kept separate

- **Authentication** — who is the user? (JWT in `Authorization: Bearer …`)
- **Authorization** — what can they do? (role check on the view)

### Role hierarchy

`apps/common/permissions.py` — `MANAGEABLE_ROLES`:

```python
MANAGEABLE_ROLES = {
    "SUPER_ADMIN": {"SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE"},
    "ADMIN": {"HR_MANAGER", "EMPLOYEE"},
    "HR_MANAGER": {"EMPLOYEE"},
    "EMPLOYEE": set(),
}
```

`can_manage_user(actor_role, target_role)` returns True if the actor may manage a target with that role. Used in employee update/delete logic.

### Resource ownership

Some endpoints need an extra check: an EMPLOYEE can only see their **own** record. Views handle this directly:

```python
record = self.service.get_leave(leave_id)
if request.user.get("role") == "EMPLOYEE" and str(record.get("employee_id")) != str(request.user["_id"]):
    return error("You do not have permission to view this leave.", status.HTTP_403_FORBIDDEN)
```

---

## 10. Permission Decorator

`apps/common/permissions.py` — `require_role(*allowed_roles)`:

```python
@require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
def post(self, request):
    # Only SUPER_ADMIN, ADMIN, HR_MANAGER can call this
    ...
```

### How it works

1. The decorator receives the allowed roles: `@require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")`.
2. It returns a `decorator(view_func)` that wraps the view method.
3. The `wrapper(view, request, *args, **kwargs)` runs when the endpoint is called.
4. It gets `request.user` (set by `JWTAuthentication`).
5. It reads `user.get("role")`.
6. If the role is not in the allowed list, it raises `PermissionDenied` (HTTP 403).
7. If the role is allowed, it calls the original view method.

### Default permission

`apps/common/permissions.py` — `IsAuthenticatedUser` is the default permission class in DRF settings. It checks that `request.user` exists and has an `_id`.

---

## 11. Employee Management

### Purpose

Create, list, update, and delete employees. Only SUPER_ADMIN, ADMIN, and HR_MANAGER can manage employees.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/employees/views.py` |
| Serializer | `apps/employees/serializers.py` |
| Service | `apps/employees/services.py` |
| URL | `apps/employees/urls.py` |
| Frontend page | `frontend/src/pages/employees/EmployeesPage.tsx` |
| Frontend service | `frontend/src/services/employee.service.ts` |

### Backend flow

```text
POST /api/employees/
   ↓
EmployeeView.post()                               apps/employees/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
   ↓ EmployeeSerializer validates
   ↓
EmployeeService.create_employee(data)             apps/employees/services.py
   ↓ validate first_name, last_name, email, password, role, phone, status
   ↓ hash_password(), generate_employee_code()
   ↓ insert into MongoDB "users"
   ↓ log_activity("EMPLOYEE", "CREATE_EMPLOYEE", ...)
   ↓
Response: { user_id: "<new ObjectId>" }
```

### Business rules

- Email must be unique (case-insensitive).
- Password must be at least 8 characters.
- Role must be one of: SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE.
- Status must be one of: ACTIVE, INACTIVE.
- Only SUPER_ADMIN can delete employees (soft delete via `is_deleted: True`).
- Update respects `can_manage_user` — an HR_MANAGER cannot edit an ADMIN.

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/employees/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Create employee |
| GET | `/api/employees/` | SUPER_ADMIN, ADMIN, HR_MANAGER | List employees (with filters + pagination) |
| GET | `/api/employees/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Get single employee |
| PUT | `/api/employees/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Update employee |
| PATCH | `/api/employees/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Update employee status |
| DELETE | `/api/employees/<id>/` | SUPER_ADMIN | Delete employee (soft delete) |

---

## 12. Employee Creation — Complete Flow

```text
Frontend employee form (EmployeesPage)
   ↓
employeeService.create(payload)                   frontend/src/services/employee.service.ts
   ↓ http.post("/employees/", payload)             frontend/src/services/api.ts
   ↓ Axios attaches JWT                            frontend/src/config/axios.ts
   ↓
POST /api/employees/
   ↓
config/urls.py → apps/employees/urls.py
   ↓
EmployeeView.post()                               apps/employees/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
   ↓ EmployeeSerializer.is_valid(raise_exception=True)
   ↓
EmployeeService.create_employee(data)             apps/employees/services.py
   ↓ validate first_name, last_name, email, password, role, phone, status
   ↓ check email uniqueness
   ↓ hash_password(password)
   ↓ generate_employee_code()                      apps/common/utils.py
   ↓
get_collection("users").insert_one(document)
   ↓
MongoDB "users" collection
   ↓
log_activity("EMPLOYEE", "CREATE_EMPLOYEE", ...) apps/activity_logs/services.py
   ↓
Response: { success, message, data: { user_id } }
   ↓
Frontend unwraps data, updates UI
```

---

## 13. Departments

### Purpose

Manage company departments. Separated into its own app.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/departments/views.py` |
| Serializer | `apps/departments/serializers.py` |
| Service | `apps/departments/services.py` |
| URL | `apps/departments/urls.py` |
| Frontend page | `frontend/src/pages/departments/DepartmentsPage.tsx` |
| Frontend service | `frontend/src/services/department.service.ts` |

### Backend flow

```text
POST /api/departments/
   ↓
DepartmentView.post()                             apps/departments/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
   ↓ DepartmentSerializer validates
   ↓
DepartmentService.create_department(data)         apps/departments/services.py
   ↓ validate name, code (both unique)
   ↓ insert into MongoDB "departments"
   ↓ log_activity("DEPARTMENT", "CREATE_DEPARTMENT", ...)
```

### Business rules

- Name must be unique (case-insensitive).
- Code must be unique (case-insensitive).
- Soft delete: `is_active = False` (cannot delete if employees are assigned).
- Unique indexes on `name` and `code`.

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/departments/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Create department |
| GET | `/api/departments/` | SUPER_ADMIN, ADMIN, HR_MANAGER | List departments |
| GET | `/api/departments/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Get single department |
| PUT | `/api/departments/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Update department |
| DELETE | `/api/departments/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Soft delete department |

---

## 14. Designations

### Purpose

Manage employee designations (job titles). Separated into its own app.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/designations/views.py` |
| Serializer | `apps/designations/serializers.py` |
| Service | `apps/designations/services.py` |
| URL | `apps/designations/urls.py` |
| Frontend page | `frontend/src/pages/designations/DesignationsPage.tsx` |
| Frontend service | `frontend/src/services/designation.service.ts` |

### Backend flow

```text
POST /api/designations/
   ↓
DesignationView.post()                            apps/designations/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
   ↓ DesignationSerializer validates
   ↓
DesignationService.create_designation(data)       apps/designations/services.py
   ↓ validate name (unique), code (unique, optional)
   ↓ insert into MongoDB "designations"
   ↓ log_activity("DESIGNATION", "CREATE_DESIGNATION", ...)
```

### Business rules

- Name must be unique (case-insensitive).
- Code is optional, but if provided must be unique.
- Code is stored uppercase.
- Unique indexes on `name` and `code`.

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/designations/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Create designation |
| GET | `/api/designations/` | SUPER_ADMIN, ADMIN, HR_MANAGER | List designations |
| GET | `/api/designations/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Get single designation |
| PUT | `/api/designations/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER | Update designation |

---

## 15. Attendance

### Purpose

Track employee attendance: manual marking, check-in, check-out, and summaries.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/attendance/views.py` |
| Serializer | `apps/attendance/serializers.py` |
| Service | `apps/attendance/services.py` |
| URL | `apps/attendance/urls.py` |
| Frontend page | `frontend/src/pages/attendance/AttendancePage.tsx` |
| Frontend service | `frontend/src/services/attendance.service.ts` |

### Backend flow

```text
POST /api/attendance/actions/check-in/
   ↓
AttendanceView.post()                             apps/attendance/views.py
   ↓ @require_role(EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN)
   ↓
AttendanceService.check_in(employee_id)           apps/attendance/services.py
   ↓ verify employee is active
   ↓ if no record for today → create with check_in = now
   ↓ if record exists without check_in → update check_in
   ↓ if already checked in → error
   ↓ log_activity("ATTENDANCE", "CHECK_IN", ...)
   ↓
MongoDB "attendance" collection
```

### Business rules

- One record per employee per day (unique index on `employee_id` + `date`).
- EMPLOYEE can only mark their own attendance.
- Check-out must follow a check-in.
- Valid statuses: PRESENT, ABSENT, HALF_DAY, LEAVE.
- Only HR_MANAGER, ADMIN, SUPER_ADMIN can update attendance records.

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/attendance/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Mark attendance |
| POST | `/api/attendance/actions/check-in/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Check-in |
| POST | `/api/attendance/actions/check-out/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Check-out |
| GET | `/api/attendance/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | List attendance (EMPLOYEE sees own only) |
| GET | `/api/attendance/<id>/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Get single record |
| PUT | `/api/attendance/<id>/` | HR_MANAGER, ADMIN, SUPER_ADMIN | Update attendance |
| GET | `/api/attendance/summary/<employee_id>/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Get summary |

---

## 16. Leave Management

### Purpose

Apply for leave, view leaves, and approve/reject leaves.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/leaves/views.py` |
| Serializer | `apps/leaves/serializers.py` |
| Service | `apps/leaves/services.py` |
| URL | `apps/leaves/urls.py` |
| Frontend page | `frontend/src/pages/leaves/LeavesPage.tsx` |
| Frontend service | `apps/leaves/services.py` |

### Apply for leave

```text
POST /api/leaves/   { start_date, end_date, leave_type, reason }
   ↓
LeaveView.post()                                  apps/leaves/views.py
   ↓ @require_role(EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN)
   ↓ if EMPLOYEE → force employee_id = current user
   ↓ LeaveSerializer validates
   ↓
LeaveService.apply_leave(data)                    apps/leaves/services.py
   ↓ check start_date <= end_date
   ↓ verify leave_type is valid
   ↓ verify employee is active
   ↓ insert leave with status = PENDING
   ↓ log_activity("LEAVE", "APPLY_LEAVE", ...)
   ↓
MongoDB "leaves" collection
```

### Approve / reject leave

```text
PUT /api/leaves/<leave_id>/   { status: "APPROVED" | "REJECTED" }
   ↓
LeaveView.put()                                   apps/leaves/views.py
   ↓ @require_role(HR_MANAGER, ADMIN, SUPER_ADMIN)
   ↓
LeaveService.update_leave_status(leave_id, status, user_id)
   ↓ only PENDING leaves can change
   ↓ you cannot approve/reject your own leave
   ↓ set approved_by or rejected_by
   ↓ log_activity("LEAVE", "APPROVE_LEAVE" | "REJECT_LEAVE", ...)
```

### Business rules

- Valid leave types: ANNUAL, SICK, CASUAL, UNPAID.
- Valid statuses: PENDING, APPROVED, REJECTED.
- EMPLOYEE can only apply for their own leaves.
- EMPLOYEE can only view their own leaves.
- Only PENDING leaves can be updated.
- You cannot approve/reject your own leave.
- Leave records are never deleted (historical data).

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/leaves/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Apply for leave |
| GET | `/api/leaves/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | List leaves |
| GET | `/api/leaves/<id>/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | Get single leave |
| PUT | `/api/leaves/<id>/` | HR_MANAGER, ADMIN, SUPER_ADMIN | Approve/reject leave |

---

## 17. Profile and Image Upload

### Purpose

View and update the current user's profile, including profile image.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/authentication/views.py` (UserView, ProfileImageView, serve_profile_image) |
| Service | `apps/authentication/services.py` (UserService, ProfileImageService) |
| Serializer | `apps/authentication/serializers.py` (UserSerializer) |
| Frontend service | `frontend/src/services/user.service.ts` |

### Profile flow

```text
GET /api/auth/me/
   ↓
UserView.get()                                    apps/authentication/views.py
   ↓
UserService.get_by_id(user_id)                    apps/authentication/services.py
   ↓
Response: UserSerializer(user).data
```

```text
PATCH /api/auth/profile/   { first_name, last_name, phone }
   ↓
UserView.patch()                                  apps/authentication/views.py
   ↓
UserService.update(user_id, updates)              apps/authentication/services.py
   ↓ log_activity("AUTHENTICATION", "PROFILE_UPDATE", ...)
```

### Image upload flow

```text
Frontend: <input type="file" />  → FormData
   ↓
POST /api/auth/profile/image/   (multipart/form-data, Authorization: Bearer <token>)
   ↓
ProfileImageView.post()                           apps/authentication/views.py
   ↓
ProfileImageService.upload(user_id, file)         apps/authentication/services.py
   ↓ validate content type (jpeg/png/webp/gif) and size (≤ 5 MB)
   ↓ delete old GridFS file (if any)
   ↓ store new file in GridFS
   ↓ save the file id in users.profile_image_id
   ↓ log_activity("AUTHENTICATION", "PROFILE_IMAGE_UPDATE", ...)
   ↓
GET /api/auth/profile/image/<user_id>/   (public, no auth)
   ↓
serve_profile_image()                             apps/authentication/views.py
   ↓ read GridFS file and stream it back as an HTTP response
```

The serve endpoint is public so `<img src="...">` tags can load avatars without attaching JWT headers.

---

## 18. Payment System

### Purpose

Office amenity payments via **Razorpay (Test Mode)**. Razorpay is the **only**
payment gateway in EmpSphere — there is no gateway selector, no fallback, and
no multi-gateway abstraction. The backend is the source of truth for amounts
and payment status; the frontend only opens Razorpay Checkout.

> Test Mode is configured by default. Live deployment is **not** claimed
> until valid live Razorpay keys are wired in and a production environment is
> set up.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/payments/views.py` |
| Serializer | `apps/payments/serializers.py` |
| Service | `apps/payments/services.py` |
| Gateway | `apps/payments/gateways.py` |
| URL | `apps/payments/urls.py` |
| Frontend page | `frontend/src/pages/payments/PaymentsPage.tsx` |
| Frontend service | `frontend/src/services/payment.service.ts` |

### Payment flow

```text
User clicks "Make Payment"
   ↓
Selects an Amenity
   ↓
POST /api/payments/   { amenity_id, employee_id? }     (no gateway field)
   ↓
PaymentView.post()                                 apps/payments/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE)
   ↓ EMPLOYEE → employee_id = self
   ↓ SUPER_ADMIN → employee_id required
   ↓ others → employee_id defaults to self
   ↓
PaymentService.create_payment(...)                 apps/payments/services.py
   ↓ look up amenity (amount comes from backend, never frontend)
   ↓ look up employee
   ↓ if a PENDING payment already exists for the same employee+amenity, reuse it
   ↓ call RazorpayGateway.create_order(amount in INR → converted to paise)
   ↓ save payment doc with status PENDING, gateway = "RAZORPAY"
   ↓ log_activity("PAYMENT", "PAYMENT_CREATED", ...)
   ↓
Response: { payment_id, order_id, amount, currency, key_id }
   ↓
Frontend loads https://checkout.razorpay.com/v1/checkout.js
   ↓ opens Razorpay Checkout with key_id, order_id, amount, currency
   ↓
User completes test payment in the Razorpay modal
   ↓
Razorpay returns { razorpay_order_id, razorpay_payment_id, razorpay_signature }
   ↓
Frontend POST /api/payments/<id>/verify/   { razorpay_order_id, razorpay_payment_id, razorpay_signature }
   ↓
PaymentService.verify_payment(...)                apps/payments/services.py
   ↓ verify Razorpay Checkout signature with RAZORPAY_KEY_SECRET
   ↓ mark payment PAID, store gateway_payment_id, set payment_date
   ↓ log_activity("PAYMENT", "PAYMENT_VERIFIED", ...)
   ↓
Razorpay also sends a webhook to /api/payments/webhook/razorpay/  (HMAC signed)
   ↓
RazorpayWebhookView verifies X-Razorpay-Signature, then updates the payment:
   status = PAID (or FAILED / PENDING for authorized)
   gateway_payment_id = razorpay payment id
   log_activity("PAYMENT", "PAYMENT_VERIFIED", ...)
   ↓ idempotent: re-deliveries for the same gateway payment id are skipped
```

### Razorpay configuration

All Razorpay credentials are loaded from `backend/.env`:

```text
RAZORPAY_KEY_ID=            # publishable, sent to the frontend
RAZORPAY_KEY_SECRET=        # backend only, used to verify Checkout signatures
RAZORPAY_WEBHOOK_SECRET=    # backend only, used to verify webhook signatures
RAZORPAY_ENVIRONMENT=TEST   # TEST or LIVE
```

- The backend issues Razorpay orders using HTTP Basic auth with the key
  id/secret pair.
- Amounts are always supplied to the gateway in **paise** (1 INR = 100 paise).
  The backend multiplies the INR amount by 100 when calling Razorpay.
- The frontend receives only `key_id` and the order details — never the
  secret or webhook secret.

### Security notes

- `RAZORPAY_KEY_SECRET` and `RAZORPAY_WEBHOOK_SECRET` live only in the backend
  `.env` and are **never** sent to the browser. Only `RAZORPAY_KEY_ID` is
  exposed to the frontend for the Razorpay Checkout widget.
- The payment amount is **always** read from the amenity record on the server
  — the frontend cannot influence it.
- Webhook requests are authenticated by HMAC-SHA256 over the raw body using
  the webhook secret before any DB update.
- A payment is only marked as PAID after the backend re-derives the
  Razorpay Checkout signature with the key secret. The frontend's report of
  success is never trusted on its own.
- A pending payment is reused (not duplicated) for the same employee + amenity.
- The webhook handler is idempotent: re-deliveries for the same gateway
  payment id, or payments already in a terminal state, are ignored.

### Status mapping

Razorpay payment statuses are mapped to EmpSphere internal statuses:

| Razorpay | EmpSphere |
|----------|-----------|
| `captured`, `succeeded`, `paid` | `PAID` |
| `authorized` | `PENDING` |
| `failed`, `error` | `FAILED` |
| `refunded` | `REFUNDED` |
| `cancelled` | `CANCELLED` |
| `created`, `pending` | `PENDING` |
| anything else | `PENDING` |

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/payments/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | Create payment |
| GET | `/api/payments/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | List payments |
| GET | `/api/payments/me/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | Get my payments |
| GET | `/api/payments/<id>/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | Get single payment |
| POST | `/api/payments/<id>/verify/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | Verify payment (Razorpay Checkout signature) |
| POST | `/api/payments/<id>/cancel/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | Cancel payment |
| GET | `/api/payments/amenities/` | SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE | List amenities |
| POST | `/api/payments/amenities/` | SUPER_ADMIN, ADMIN | Create amenity |
| PUT | `/api/payments/amenities/<id>/` | SUPER_ADMIN, ADMIN | Update amenity |
| DELETE | `/api/payments/amenities/<id>/` | SUPER_ADMIN, ADMIN | Soft delete amenity |
| POST | `/api/payments/webhook/razorpay/` | Public (HMAC signed) | Razorpay webhook |
| GET | `/api/payments/callback/` | Public | Razorpay redirect |

---

## 19. Activity Logs

### Purpose

A single reusable audit log function used by every module to record what happened.

### Important files

| Purpose | File |
|---------|------|
| Log function | `apps/activity_logs/services.py` |
| View | `apps/activity_logs/views.py` |
| URL | `apps/activity_logs/urls.py` |
| Frontend page | `frontend/src/pages/activityLogs/ActivityLogsPage.tsx` |
| Frontend service | `frontend/src/services/activityLog.service.ts` |

### How it works

```python
from apps.activity_logs.services import log_activity

log_activity(
    module="EMPLOYEE",
    action="CREATE_EMPLOYEE",
    performed_by=str(user_id),
    target_id=str(new_employee_id),
    status="SUCCESS",
    description="Created employee John Doe (john@example.com).",
)
```

The function inserts a document into the `activity_logs` collection:

```text
log_activity(module, action, performed_by, target_id, status, description, metadata)
   ↓
get_collection("activity_logs").insert_one({
    "module", "action", "performed_by", "target_id",
    "status", "description", "metadata", "created_at"
})
   ↓
MongoDB "activity_logs" collection
```

### What fields are stored

| Field | Description |
|-------|-------------|
| `module` | Which area (EMPLOYEE, LEAVE, PAYMENT, AUTHENTICATION, ...) |
| `action` | What happened (CREATE_EMPLOYEE, APPROVE_LEAVE, LOGIN, ...) |
| `performed_by` | User ID who did the action |
| `target_id` | The affected record's ID |
| `status` | SUCCESS or FAILED |
| `description` | Human-readable message |
| `metadata` | Optional extra dict |
| `created_at` | Timestamp |

### Who can access logs

- EMPLOYEE — only their own logs.
- HR_MANAGER / ADMIN — logs of users they can manage.
- SUPER_ADMIN — all logs.
- Logs are filtered to the last 30 days.

### API endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| GET | `/api/activity-logs/` | EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN | List activity logs |
| GET | `/api/activity-logs/actions/` | Any authenticated user | List distinct actions |

---

## 20. Reports

### Purpose

Generate management reports with summaries and filtered record lists.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/reports/views.py` |
| Service | `apps/reports/services.py` |
| URL | `apps/reports/urls.py` |
| Frontend page | `frontend/src/pages/reports/ReportsPage.tsx` |
| Frontend service | `frontend/src/services/report.service.ts` |

### Available reports

| Report | URL | Description |
|--------|-----|-------------|
| Employees | `/api/reports/employees/` | Employee list + summary (by department, designation, role) |
| Attendance | `/api/reports/attendance/` | Attendance records + summary (present/absent/half/leave) |
| Leaves | `/api/reports/leaves/` | Leave records + summary (pending/approved/rejected, by type) |
| Departments | `/api/reports/departments/` | Department list + summary |
| Designations | `/api/reports/designations/` | Designation list + summary |
| Activity | `/api/reports/activity/` | Activity log records + summary (by action, by module) |

### Backend flow

```text
GET /api/reports/employees/?department_id=...&status=...
   ↓
ReportView.get()                                  apps/reports/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
   ↓
ReportService.get_employee_report(filters)        apps/reports/services.py
   ↓ build query from filters
   ↓ get summary (counts) + records (paginated)
   ↓ log_activity("REPORTS", "GENERATE_REPORT", ...)
   ↓
Response: { summary, records, meta: { page, page_size, total_records, total_pages } }
```

---

## 21. Statistics and Dashboards

### Purpose

Provide summary counts for the dashboard.

### Important files

| Purpose | File |
|---------|------|
| View | `apps/statistics/views.py` |
| Service | `apps/statistics/services.py` |
| URL | `apps/statistics/urls.py` |
| Frontend page | `frontend/src/pages/dashboard/DashboardPage.tsx` |
| Frontend service | `frontend/src/services/statistics.service.ts` |

### Backend flow

```text
GET /api/statistics/
   ↓
StatisticsView.get()                              apps/statistics/views.py
   ↓ @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE)
   ↓
StatisticsService.get_dashboard_stats()           apps/statistics/services.py
   ↓ count users, departments, attendance, pending leaves
   ↓
Response: { total_employees, total_departments, total_attendance, pending_leaves }
```

---

## 22. MongoDB

### Connection

`apps/common/database.py` — single shared connection:

```python
from pymongo import MongoClient
_client = MongoClient(settings.MONGO_URI, ...)
mongo: Database = _client[settings.DATABASE_name]

def get_collection(name: str):
    return mongo[name]
```

### Collections

Defined in `apps/common/constants.py` — `class Collections`:

| Collection | Holds |
|-----------|-------|
| `users` | Employee and admin accounts (every role) |
| `roles` | Role documents (SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE) |
| `permissions` | Permission documents |
| `tokens` | Blacklisted refresh tokens |
| `otps` | One-time passwords |
| `departments` | Departments |
| `designations` | Designations |
| `attendance` | Attendance records |
| `leaves` | Leave applications |
| `payments` | Payment records |
| `amenities` | Office amenities (name, amount) |
| `activity_logs` | Audit log entries |

### Important behaviors

- Document IDs are `ObjectId`; all APIs return IDs as **strings**.
- Soft delete: employees use `is_active: False, is_deleted: True`; departments and amenities use `is_active: False`.
- Timestamps: `created_at`, `updated_at` stored as UTC datetime.
- Unique indexes are created in service `__init__` methods (e.g., employee email, department name/code).

---

## 23. Axios and API Communication

### Axios instance

`frontend/src/config/axios.ts`:

```text
baseURL: ENV.API_BASE_URL   (default: http://127.0.0.1:8000/api)
```

### Request interceptor

- Attaches `Authorization: Bearer <access_token>` to every request.
- Skips public endpoints: `/auth/login/`, `/auth/register/`, `/auth/logout/`, `/auth/refresh-token/`, `/auth/verify-email/`, `/auth/google-login/`, `/auth/send-otp/`, `/auth/verify-otp/`, `/auth/set-password/`.

### Response interceptor (401 handling)

```text
Request → 401 Unauthorized
   ↓
if not already retried and not a public endpoint:
   ↓ POST /auth/refresh-token/ with { refresh_token }
   ↓ on success: save new access + refresh tokens, retry original request
   ↓ on failure: clear tokens, dispatch "auth:expired" event → redirect to /login
```

### http wrapper

`frontend/src/services/api.ts`:

- `http.get()`, `http.post()`, `http.put()`, `http.patch()`, `http.delete()`.
- Each unwraps the backend's `{success, message, data}` envelope via `unwrap()` — returns only the `data` field.

### Token storage

`frontend/src/utils/token.ts` — `TokenUtil`:

- Access token stored in `localStorage` under `emp_access_token`.
- Refresh token stored under `emp_refresh_token`.
- `setTokens()`, `getAccessToken()`, `getRefreshToken()`, `clear()`.

---

## 24. Environment Variables

### Backend — `backend/.env`

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Django secret key | dev-only fallback |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` |
| `MONGO_URI` | MongoDB connection URI | `mongodb://localhost:27017` |
| `DATABASE_NAME` | MongoDB database name | `empsphere_db` |
| `JWT_SECRET` | JWT signing secret | falls back to `SECRET_KEY` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXP_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXP_DAYS` | Refresh token lifetime | `7` |
| `PASSWORD_RESET_TOKEN_EXP_MINUTES` | Reset token lifetime | `10` |
| `EMAIL_HOST` | SMTP host | `` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username | `` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | `` |
| `GOOGLE_REDIRECT_URI` | Google redirect URI | `` |
| `RAZORPAY_KEY_ID` | Razorpay publishable key id | `` |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret (backend only) | `` |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook secret (backend only) | `` |
| `RAZORPAY_ENVIRONMENT` | Razorpay environment label | `TEST` |
| `COMPANY_REGISTRATION_SECRET` | Required for registration | `` |
| `FRONTEND_URL` | Frontend URL (CORS) | `http://localhost:3000` |
| `BACKEND_URL` | Backend URL (webhooks) | `http://localhost:8000` |

### Frontend — `frontend/.env`

| Variable | Purpose | Default |
|----------|---------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://127.0.0.1:8000/api` |
| `VITE_APP_URL` | Frontend app URL | `http://localhost:3000` |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID | (empty) |
| `VITE_RAZORPAY_KEY_ID` | Razorpay publishable key id (frontend-safe) | (empty) |

---

## 25. Running the Project

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB running locally (or a remote URI)

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Edit backend/.env (SECRET_KEY, JWT_SECRET, MONGO_URI, EMAIL_*, GOOGLE_*, RAZORPAY_*)

.\venv\Scripts\python.exe manage.py seed_rbac
.\venv\Scripts\python.exe manage.py seed_amenities
.\venv\Scripts\python.exe manage.py runserver
```

Backend runs at `http://localhost:8000`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
# Edit frontend/.env: VITE_API_BASE_URL, VITE_GOOGLE_CLIENT_ID (optional)
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## 26. Verification

```powershell
# Backend
cd backend
.\venv\Scripts\python.exe manage.py check

# Frontend
cd frontend
npx tsc --noEmit
npm run build
```

---

## 27. Debugging Guide

| Error | What it means | Where to look | Common cause in THIS project |
|-------|---------------|---------------|----------------------------|
| **400 Bad Request** | Invalid input | Serializer errors in response body | Field name mismatch, missing required field, invalid email format |
| **401 Unauthorized** | JWT missing / expired | `apps/common/authentication.ts`, `config/axios.ts` | Token expired and refresh failed; check `JWT_SECRET` consistency |
| **403 Forbidden** | Wrong role | `@require_role` decorator, `apps/common/permissions.py` | User role not in allowed list; trying to access another user's record |
| **404 Not Found** | Resource not found | Service layer `find_one()` | Invalid ObjectId, or record was soft-deleted |
| **500 Internal Server Error** | Unhandled exception | `backend/logs/app.log`, terminal traceback | Unexpected error caught by `ExceptionMiddleware` |
| **CORS error** | Cross-origin blocked | `config/settings.py` `CORS_ALLOWED_ORIGINS` | `FRONTEND_URL` not matching the actual frontend origin |
| **MongoDB connection** | Cannot connect to DB | `apps/common/database.py` | MongoDB not running, wrong `MONGO_URI` |
| **JWT invalid** | Token verification failed | `apps/common/authentication.py` | Wrong `JWT_SECRET`, expired token, tampered token |
| **OTP expired** | OTP no longer valid | `apps/authentication/services.py` | OTP lifetime is 10 minutes; user took too long |
| **Image upload fails** | File rejected | `ProfileImageService.validate_file()` | Wrong content type (not jpeg/png/webp/gif) or > 5 MB |
| **Payment fails** | Razorpay error | `apps/payments/gateways.py`, `apps/payments/services.py` | Wrong Razorpay credentials, sandbox unreachable |
| **Frontend TypeScript** | Type error | `tsconfig.json`, terminal output | Missing type, wrong import path, `noUnusedLocals` violation |
| **Build errors** | Vite/tsc failure | Terminal output | TypeScript errors, missing dependencies |
| **API connection** | Frontend cannot reach backend | `frontend/src/config/env.ts` | Wrong `VITE_API_BASE_URL`, backend not running |

---

## 28. Deployment

There is no Vercel configuration in the current project. The CI pipeline (`.github/workflows/ci-backend.yml`) runs backend tests against MongoDB on push/PR. Deployment architecture is not defined in the codebase — you would need to configure this separately.

---

## 29. Safe Development Rules

1. **Never modify code** when asked to document — document what exists.
2. **Never commit secrets** — `.env` files are gitignored.
3. **Never trust the frontend for payment amounts** — the backend always reads the amount from the amenity record.
4. **Never delete leave records** — they are historical business data.
5. **Never approve your own leave** — enforced in the service layer.
6. **Never expose `RAZORPAY_KEY_SECRET` or `RAZORPAY_WEBHOOK_SECRET`** — they live only in the backend `.env`.
7. **Never skip `seed_rbac`** — you need the Super Admin user and roles to start.
8. **Never use frontend role checks alone** — the backend always re-checks roles via `@require_role`.

---

## 30. Fresher Learning Path

Read in this order:

1. `docs/PROJECT_GUIDE.md` (this file) — top to bottom.
2. `backend/config/settings.py` and `config/urls.py`.
3. `backend/apps/common/constants.py` — collections, roles, OTP policy.
4. `backend/apps/common/database.py` — how MongoDB is connected.
5. `backend/apps/common/authentication.py` — the JWT auth class.
6. `backend/apps/common/permissions.py` — the role decorator.
7. `backend/apps/authentication/services.py` — the `login` method.
8. `backend/apps/employees/services.py` — `create_employee`.
9. `backend/apps/leaves/services.py` — `apply_leave` and `update_leave_status`.
10. `frontend/src/config/axios.ts` — the JWT interceptor.
11. `frontend/src/services/auth.service.ts` — how the frontend calls the backend.
12. `frontend/src/store/slices/authSlice.ts` — how the user is stored in Redux.
13. `frontend/src/routes/AppRoutes.tsx` — how routes are protected.

That's the whole codebase. There is no magic — each piece is small and does one thing.

---

## 31. Quick File Reference

### Where is the code?

| Question | Answer |
|----------|--------|
| Employee creation | `apps/employees/services.py` → `create_employee()` |
| JWT checked | `apps/common/authentication.py` → `JWTAuthentication.authenticate()` |
| Permission decorator | `apps/common/permissions.py` → `require_role()` |
| Role received | `request.user.get("role")` (set by JWT auth) |
| Leave approval | `apps/leaves/services.py` → `update_leave_status()` |
| Image upload | `apps/authentication/services.py` → `ProfileImageService.upload()` |
| Payment verification | `apps/payments/services.py` → `verify_payment()` |
| Activity logging | `apps/activity_logs/services.py` → `log_activity()` |
| Axios configured | `frontend/src/config/axios.ts` |
| Token refresh | `frontend/src/config/axios.ts` (response interceptor) |
| MongoDB connection | `apps/common/database.py` |
| Response helpers | `apps/common/responses.py` → `success()` / `error()` |
| Password hashing | `apps/common/utils.py` → `hash_password()` |
| Employee code generation | `apps/common/utils.py` → `generate_employee_code()` |
| Token blacklist | `apps/authentication/services.py` → `blacklist_token()` |
| Settings object | `apps/common/settings.py` → `settings` |
| Frontend token storage | `frontend/src/utils/token.ts` → `TokenUtil` |
| Frontend auth state | `frontend/src/store/slices/authSlice.ts` |
| Frontend route guards | `frontend/src/routes/ProtectedRoute.tsx`, `RequireRole.tsx` |

---

## 32. How EmpSphere Works — Final Summary

```text
User opens browser
       ↓
React app loads (main.tsx → App.tsx)
       ↓
AppBootstrap checks for stored JWT → dispatches fetchMe
       ↓
User sees dashboard (role-specific)
       ↓
User performs an action (create employee, apply leave, ...)
       ↓
Frontend service calls backend via Axios
       ↓
Axios attaches JWT (except public endpoints)
       ↓
Django routes the request to the correct view
       ↓
JWTAuthentication decodes the token → loads user from MongoDB
       ↓
@require_role checks the user's role
       ↓
Serializer validates the request body
       ↓
Service executes business logic
       ↓
MongoDB stores/retrieves data
       ↓
Activity log records what happened
       ↓
Response flows back: { success, message, data }
       ↓
Frontend unwraps data, updates UI
```

Every feature follows this same pattern. Once you understand one module, you understand them all.