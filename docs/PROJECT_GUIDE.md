# EmpSphere — Complete Project Guide

A beginner-friendly guide to understanding the EmpSphere employee management system.

---

## Table of Contents

1. [What is EmpSphere?](#1-what-is-empsphere)
2. [Why does it exist?](#2-why-does-it-exist)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Architecture Overview](#5-architecture-overview)
6. [Backend Deep Dive](#6-backend-deep-dive)
7. [Frontend Deep Dive](#7-frontend-deep-dive)
8. [Database — MongoDB](#8-database--mongodb)
9. [Authentication](#9-authentication)
10. [Authorization / RBAC](#10-authorization--rbac)
11. [Employee Management](#11-employee-management)
12. [Organization — Departments & Designations](#12-organization--departments--designations)
13. [Attendance](#13-attendance)
14. [Leave Management](#14-leave-management)
15. [Payment System — Cashfree Sandbox](#15-payment-system--cashfree-sandbox)
16. [Activity Logs](#16-activity-logs)
17. [Reports](#17-reports)
18. [Statistics / Dashboard](#18-statistics--dashboard)
19. [Environment Variables](#19-environment-variables)
20. [Running the Project](#20-running-the-project)
21. [Cashfree Sandbox Setup](#21-cashfree-sandbox-setup)
22. [Debugging Guide](#22-debugging-guide)
23. [Verification](#23-verification)
24. [Deployment](#24-deployment)
25. [Safe Future Development](#25-safe-future-development)
26. [Fresher Learning Path](#26-fresher-learning-path)
27. [How EmpSphere Works (Summary)](#27-how-empsphere-works-summary)

---

## 1. What is EmpSphere?

EmpSphere is a **full-stack Employee Management System (EMS)**. It helps organizations manage:

- Employee records
- Departments and designations
- Attendance (check-in / check-out)
- Leave applications and approvals
- Office amenity payments (via Cashfree)
- Activity logging and audit trails
- Reports and dashboard statistics

The system enforces **Role-Based Access Control (RBAC)** so that different users see only what they are allowed to see.

---

## 2. Why does it exist?

Managing employees with spreadsheets or paper records is error-prone and hard to audit. EmpSphere provides:

- A **single source of truth** for employee data (MongoDB).
- **Role-based access** so employees, HR, admins, and super admins each see only their relevant data.
- **Audit trails** (activity logs) so every important action is recorded.
- **Automated attendance and leave workflows** instead of manual tracking.
- **Digital payments** for office amenities via Cashfree.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend framework | Django 4.2 + Django REST Framework | HTTP API, request handling |
| Backend language | Python 3.8+ | Business logic |
| Database driver | PyMongo | Talk to MongoDB |
| Auth tokens | PyJWT | JSON Web Tokens |
| Config | python-dotenv | Load `.env` variables |
| Frontend framework | React 18 + TypeScript | UI |
| Build tool | Vite 5 | Fast dev server and production build |
| State management | Redux Toolkit | Global application state |
| Routing | React Router v7 | Page navigation |
| HTTP client | Axios | API calls to backend |
| Styling | Tailwind CSS | Utility-first CSS |
| Database | MongoDB | Primary data store |
| Django internal DB | SQLite (in-memory) | Django's internal tables |
| Payments | Cashfree (Sandbox) | Office amenity payments |

---

## 4. Project Structure

```
EmpSphere/
├── backend/                  # Django REST API
│   ├── config/               # Django project settings, URLs, WSGI/ASGI
│   ├── apps/                 # All business modules
│   │   ├── authentication/   # Login, register, JWT, OTP, password, Google
│   │   ├── common/           # Shared utilities (middleware, base classes, RBAC)
│   │   ├── employee/         # Employee CRUD
│   │   ├── organization/     # Departments and designations
│   │   ├── attendance/       # Check-in / check-out
│   │   ├── leave/            # Leave apply / approve
│   │   ├── payment/          # Cashfree payments + amenities
│   │   ├── activity_logs/    # Audit trail
│   │   ├── reports/          # Management reports
│   │   └── statistics/       # Dashboard statistics
│   ├── manage.py             # Django management command
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Backend secrets (gitignored)
├── frontend/                 # React + TypeScript SPA
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route-level page components
│   │   ├── routes/           # Route definitions and guards
│   │   ├── services/         # API service functions
│   │   ├── hooks/            # Custom React hooks
│   │   ├── store/            # Redux store and slices
│   │   ├── types/            # TypeScript type definitions
│   │   ├── utils/            # Helpers, constants, token storage
│   │   └── config/           # Axios config, env config
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend config (gitignored)
├── docs/                     # Documentation (this file)
├── .github/workflows/        # CI pipeline
├── README.md                 # Project overview
└── .gitignore                # Git ignore rules
```

### Backend Folder Details

Each backend module (e.g., `employee/`, `attendance/`) follows the same layered structure:

```
employee/
├── controllers/      # Handle HTTP requests/responses
├── services/         # Business logic
├── repositories/     # Database access (MongoDB)
├── serializers/      # Validate and normalize request data
├── validators/       # Input validation rules
├── dtos/             # Data Transfer Objects (typed data containers)
└── urls.py           # Module URL routes
```

### Frontend Folder Details

```
src/
├── components/       # Reusable UI (buttons, modals, forms, layout)
│   ├── common/       # Shared components (Button, Modal, Loader, etc.)
│   ├── auth/         # Auth forms (Login, Register, ForgotPassword, etc.)
│   ├── layout/       # DashboardLayout, Sidebar, Navbar
│   └── ...           # Feature-specific form modals
├── pages/            # One folder per feature (employees, attendance, etc.)
├── routes/           # AppRoutes, ProtectedRoute, RequireRole
├── services/         # One service file per feature (API calls)
├── hooks/            # One hook per feature (useAuth, useEmployees, etc.)
├── store/
│   ├── slices/       # Redux slices (auth, employee, payment, etc.)
│   └── middleware/   # Auth middleware
├── types/            # TypeScript interfaces per feature
├── utils/            # Constants, token helpers, CSV export, env
└── config/           # Axios instance, env loader
```

---

## 5. Architecture Overview

EmpSphere uses a **layered architecture** that separates concerns clearly.

### Backend Flow

```
HTTP Request
    ↓
Django URL (config/urls.py → apps/*/urls.py)
    ↓
Controller (apps/*/controllers/*)
    ↓  handles HTTP, extracts data, returns response
Serializer / Validator
    ↓  validates and normalizes request data
Service (apps/*/services/*)
    ↓  contains business logic
Repository (apps/*/repositories/*)
    ↓  talks to MongoDB
MongoDB
```

**Why this separation?**

- **Controller** — knows about HTTP only. It extracts request data and returns a response. No business logic.
- **Serializer** — validates incoming data. Ensures the service never receives bad data.
- **Service** — contains all business rules. This is where decisions are made (e.g., "an employee cannot approve their own leave").
- **Repository** — knows about MongoDB only. It performs queries and returns raw documents.
- **MongoDB** — stores the data.

### Frontend Flow

```
User clicks a button
    ↓
React component handles the event
    ↓
Hook function executes (e.g., usePayment)
    ↓
Redux slice dispatches an async thunk
    ↓
Service calls Axios
    ↓
Axios sends HTTP request to Django
    ↓
Backend processes (Controller → Service → Repository → MongoDB)
    ↓
Backend returns JSON response
    ↓
Axios receives response
    ↓
Redux slice updates state
    ↓
React re-renders the UI
```

---

## 6. Backend Deep Dive

### 6.1 config/ — Django Project Configuration

- **`config/settings.py`** — Main Django settings. Loads `.env`, configures installed apps, middleware, REST framework, JWT, email, CORS, and logging.
- **`config/urls.py`** — Root URL configuration. Routes `/api/auth/`, `/api/employees/`, `/api/payment/`, etc. to their respective modules.

### 6.2 apps/common/ — Shared Utilities

This module contains code reused across the entire backend.

| Folder | Purpose |
|--------|---------|
| `base/` | `BaseController`, `BaseService`, `BaseManager` — parent classes for all controllers/services/managers |
| `config/settings.py` | Centralized settings object that reads all `.env` variables |
| `core/` | `roles.py` (Role enum), `permissions.py` (permission constants + mapping), `collections.py` (MongoDB collection names), `status.py` (HTTP status codes) |
| `database/mongo.py` | Singleton MongoDB connection (`mongo` instance) |
| `decorators/permission.py` | `@require_role(...)` decorator for controller authorization |
| `permissions/role_permission.py` | `RolePermission` helper — hierarchy checks, `can_manage_user`, `owns_resource` |
| `middleware/` | `JWTAuthentication` (custom DRF auth), `ExceptionMiddleware`, `RequestLoggerMiddleware` |
| `exceptions/` | Custom exception classes and a global exception handler |
| `responses/api_response.py` | `ApiResponse` — consistent JSON response format (`{ success, message, data, meta }`) |
| `security/` | `PasswordManager` (bcrypt hashing), `GoogleManager` (Google OAuth token verification) |
| `management/commands/` | `seed_rbac` (creates roles, permissions, super admin), `seed_amenities` (creates test amenities) |

### 6.3 Request Flow Example (Creating an Employee)

```
POST /api/employees/
    ↓
config/urls.py → apps/employee/urls.py
    ↓
EmployeeController.post()                     [apps/employee/controllers/employee_controller.py]
    ↓  @require_role(SUPER_ADMIN, ADMIN, HR_MANAGER)
    ↓  EmployeeSerializer validates data
    ↓  Creates EmployeeDTO
    ↓
EmployeeService.create_employee(dto)          [apps/employee/services/employee_service.py]
    ↓  Business logic, validation
    ↓
EmployeeRepository.create(document)           [apps/employee/repositories/employee_repository.py]
    ↓  mongo.get_collection("users").insert_one(...)
    ↓
MongoDB "users" collection
    ↓
Response flows back: Service → Controller → JSON response
```

---

## 7. Frontend Deep Dive

### 7.1 Entry Point

- **`main.tsx`** — React entry point. Renders `<App />` into the DOM.
- **`App.tsx`** — Root component. Composes:
  - `Provider` (Redux store)
  - `BrowserRouter` (client-side routing)
  - `ToastProvider` (global notifications)
  - `AppBootstrap` (restores session on load)
  - `AppRoutes` (all route definitions)

### 7.2 Routes

- **`routes/AppRoutes.tsx`** — Declares all routes. Public routes (`/login`, `/register`) are open. Protected routes are wrapped in `ProtectedRoute` + `DashboardLayout`. Role-specific routes add `RequireRole`.
- **`routes/ProtectedRoute.tsx`** — Checks authentication. Redirects to `/login` if not authenticated.
- **`routes/RequireRole.tsx`** — Checks the user's role. Redirects to the user's dashboard if unauthorized.
- **`routes/DashboardRedirect.tsx`** — Redirects `/dashboard` to the role-specific dashboard.

### 7.3 State Management (Redux)

- **`store/index.ts`** — Configures the Redux store with slices: `auth`, `department`, `designation`, `employee`, `attendance`, `leave`, `payment`.
- **`store/slices/authSlice.ts`** — Auth state: user, loading, initializing, error. Async thunks: `login`, `register`, `fetchMe`, `logoutUser`, `googleLogin`, `completeFirstLogin`.
- **`store/slices/paymentSlice.ts`** — Payment state and thunks: `fetchPayments`, `createPayment`, `verifyPayment`, `cancelPayment`, `fetchMyPayments`, `fetchAmenities`.
- **`store/middleware/authMiddleware.ts`** — Listens for auth events.

### 7.4 API Communication

- **`config/axios.ts`** — Configured Axios instance. Attaches the access token to every request. Automatically refreshes the token on 401 errors.
- **`config/env.ts`** — Reads `VITE_*` environment variables.
- **`services/api.ts`** — Generic `http` wrapper that unwraps the standard API response envelope.
- **`services/payment.service.ts`** — Payment-specific API calls: `create`, `list`, `verify`, `cancel`, `getMyPayments`, `getAmenities`.
- **`services/auth.service.ts`** — Auth-specific API calls: `login`, `register`, `googleLogin`, `logout`, `sendOtp`, `verifyOtp`, `setPassword`, `forgotPassword`, `resetPassword`.

### 7.5 Hooks

- **`hooks/useAuth.ts`** — Provides `user`, `isAuthenticated`, `login`, `logout`, `fetchMe`, etc.
- **`hooks/usePayment.ts`** — Provides payment state and actions (`list`, `create`, `verify`, `cancel`, `loadAmenities`).
- **`hooks/useEmployees.ts`**, **`useAttendance.ts`**, **`useLeaves.ts`**, etc. — Feature-specific hooks.

### 7.6 Token Storage

- **`utils/token.ts`** — `TokenUtil` reads/writes JWT tokens to `localStorage`. Keys: `emp_access_token`, `emp_refresh_token`.

---

## 8. Database — MongoDB

EmpSphere uses **MongoDB** as its primary data store. Django's SQLite is used only for internal Django tables (in-memory).

### Connection

- **`apps/common/database/mongo.py`** — `MongoConnection` singleton. Connects using `MONGO_URI` from `.env`. Database name from `DATABASE_NAME`.

### Collections

Defined in **`apps/common/core/collections.py`**:

| Collection | Purpose |
|-----------|---------|
| `users` | Employee and admin accounts (all roles) |
| `roles` | Role documents (SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE) |
| `permissions` | Permission documents |
| `tokens` | Token-related data |
| `otps` | One-time passwords for verification |
| `departments` | Department records |
| `designations` | Designation records |
| `attendance` | Attendance records (check-in/check-out) |
| `leaves` | Leave applications |
| `payments` | Payment records |
| `amenities` | Office amenity configurations (name, amount) |
| `activity_logs` | Audit trail entries |

### Key Principles

- All repositories use the `mongo` singleton to access collections.
- Collection names are centralized in `Collections` class — never hardcoded in repositories.
- Documents use `is_deleted` for soft delete and `is_active` for status.
- Timestamps: `created_at`, `updated_at`, `deleted_at`.

---

## 9. Authentication

EmpSphere uses **JWT (JSON Web Token)** authentication with access + refresh tokens.

### Token Flow

1. User logs in with email/password.
2. Backend verifies credentials against MongoDB.
3. Backend returns an **access token** (short-lived) and a **refresh token** (longer-lived).
4. Frontend stores both tokens in `localStorage`.
5. Every API request sends the access token in the `Authorization: Bearer <token>` header.
6. When the access token expires, the frontend uses the refresh token to get a new one.
7. The old refresh token is **blacklisted** (rotated) for security.

### Authentication Files

| File | Purpose |
|------|---------|
| `apps/authentication/views/auth_view.py` | Register, login, logout endpoints |
| `apps/authentication/services/auth_service.py` | Authentication business logic |
| `apps/authentication/serializers/auth_serializer.py` | Validates login/register input |
| `apps/authentication/views/refresh_token_view.py` | Token refresh endpoint |
| `apps/authentication/views/google_login_view.py` | Google OAuth login |
| `apps/authentication/views/otp_view.py` | Send and verify OTP |
| `apps/authentication/views/verify_email_view.py` | Email verification |
| `apps/authentication/views/password_view.py` | Change/set/forgot/reset password |
| `apps/authentication/services/otp_service.py` | OTP generation and verification |
| `apps/authentication/services/password_service.py` | Password operations |
| `apps/authentication/managers/token_blacklist_manager.py` | Blacklists refresh tokens |
| `apps/authentication/managers/employee_code_manager.py` | Generates unique employee codes |
| `apps/common/middleware/authentication.py` | `JWTAuthentication` — validates tokens on every request |
| `apps/common/security/password_manager.py` | bcrypt password hashing and verification |
| `apps/common/security/google_manager.py` | Google ID token verification |

### Auth Features

- **Register** — Creates an ADMIN account. Requires a `company_secret` from `.env`. Sends email verification OTP.
- **Login** — Verifies email + password. If email is unverified, returns `requires_otp: true` instead of tokens.
- **Email Verification** — OTP sent to email. Verified via `/verify-email/` or `/verify-otp/`.
- **Google Login** — Authenticates with a Google ID token. Links to existing account by email.
- **Refresh Token** — Rotates the refresh token and blacklists the old one.
- **Logout** — Blacklists the refresh token and clears local auth state.
- **Forgot Password** — Sends OTP, verifies it, returns a reset token, then resets the password.
- **Change Password** — Authenticated user changes their own password.
- **Set Password** — Google-authenticated user sets a local password (requires OTP).
- **Profile** — View and update profile, upload profile image.

---

## 10. Authorization / RBAC

### Roles

Defined in **`apps/common/core/roles.py`**:

| Role | Level | Description |
|------|-------|-------------|
| `SUPER_ADMIN` | 4 (highest) | Full system access |
| `ADMIN` | 3 | Manages HR managers and employees |
| `HR_MANAGER` | 2 | Manages employees |
| `EMPLOYEE` | 1 (lowest) | Can manage own data only |

### Key Concepts

- **Authentication** = Who are you? (JWT token identifies the user)
- **Authorization** = What are you allowed to do? (Role determines permissions)

### Backend Enforcement

- **`@require_role(Role.ADMIN, Role.SUPER_ADMIN)`** decorator on controller methods. Returns 403 if the user's role is not in the allowed list.
- **`RolePermission.has_privilege(user_role, required_role)`** — Checks if a role is at least as privileged as required (hierarchy-based).
- **`RolePermission.can_manage_user(actor, target)`** — Checks if the actor can manage a user with the target role. SUPER_ADMIN manages everyone; ADMIN manages HR + Employee; HR manages Employee only.
- **Resource ownership** — Employees can only access their own records (checked in controllers and services).

### Frontend Enforcement

- **`ProtectedRoute`** — Redirects unauthenticated users to `/login`.
- **`RequireRole`** — Redirects unauthorized users to their own dashboard.
- **`EMPLOYEE_MANAGEMENT_ROLES`** constant in `utils/constants.ts` — Single source of truth for which roles can manage employees.

### Capability Table (from actual source code)

| Action | SUPER_ADMIN | ADMIN | HR_MANAGER | EMPLOYEE |
|--------|:-----------:|:-----:|:----------:|:--------:|
| Manage users (create/read/update) | ✅ | ✅ | ❌ | ❌ |
| Delete users | ✅ | ❌ | ❌ | ❌ |
| Manage roles | ✅ | ❌ | ❌ | ❌ |
| Manage departments | ✅ | ✅ | ❌ | ❌ |
| Read departments | ✅ | ✅ | ✅ | ❌ |
| Manage designations | ✅ | ✅ | ❌ | ❌ |
| Manage employees | ✅ | ✅ | ✅ | ❌ |
| Read employees | ✅ | ✅ | ✅ | ❌ |
| Mark attendance | ✅ | ✅ | ✅ | ✅ |
| Update attendance | ✅ | ✅ | ✅ | ❌ |
| Read attendance | ✅ | ✅ | ✅ | ✅ (own only) |
| Apply for leave | ✅ | ✅ | ✅ | ✅ |
| Approve/reject leave | ✅ | ✅ | ✅ | ❌ |
| Read leaves | ✅ | ✅ | ✅ | ✅ (own only) |
| Create payment | ✅ | ✅ | ✅ | ✅ |
| Read payments | ✅ | ✅ | ✅ | ✅ (own only) |
| Verify payments | ✅ | ✅ | ❌ | ❌ |
| View reports | ✅ | ✅ | ✅ | ❌ |
| Export reports | ✅ | ✅ | ❌ | ❌ |
| View activity logs | ✅ | ✅ | ✅ | ✅ (own only) |

---

## 11. Employee Management

### Purpose

Manages employee records — create, read, update, status changes, and delete.

### Flow

```
Frontend: EmployeesPage → useEmployees hook → employeeService → Axios
    ↓
Backend: /api/employees/ → EmployeeController → EmployeeService → EmployeeRepository → MongoDB "users"
```

### Files

| Layer | File |
|-------|------|
| Controller | `apps/employee/controllers/employee_controller.py` |
| Service | `apps/employee/services/employee_service.py` |
| Repository | `apps/employee/repositories/employee_repository.py` |
| Serializer | `apps/employee/serializers/employee_serializer.py` |
| Validator | `apps/employee/validators/employee_validator.py` |
| DTO | `apps/employee/dtos/employee_dto.py` |
| Frontend page | `frontend/src/pages/employees/EmployeesPage.tsx` |
| Frontend service | `frontend/src/services/employee.service.ts` |
| Frontend hook | `frontend/src/hooks/useEmployees.ts` |

### Business Rules

- Only `SUPER_ADMIN`, `ADMIN`, and `HR_MANAGER` can access employee management.
- Employees read their own record through the **Profile** endpoint, not Employee Management.
- Delete is `SUPER_ADMIN`-only.
- Employee status can be `ACTIVE` or `INACTIVE`.
- Each employee has a unique `employee_code` (auto-generated).

---

## 12. Organization — Departments & Designations

### Purpose

Manages the organizational structure: departments (e.g., Engineering, HR) and designations (e.g., Software Engineer, Manager).

### Files

| Layer | Department | Designation |
|-------|-----------|-------------|
| Controller | `organization/controllers/department_controller.py` | `organization/controllers/designation_controller.py` |
| Service | `organization/services/department_service.py` | `organization/services/designation_service.py` |
| Repository | `organization/repositories/department_repository.py` | `organization/repositories/designation_repository.py` |
| Serializer | `organization/serializers/department_serializer.py` | `organization/serializers/designation_serializer.py` |

### Business Rules

- Only `SUPER_ADMIN`, `ADMIN`, and `HR_MANAGER` can manage departments/designations.
- Departments and designations can be soft-deleted.
- Employees reference departments and designations by ID.

---

## 13. Attendance

### Purpose

Tracks employee attendance — check-in, check-out, and manual marking.

### Flow

```
Frontend: AttendancePage → useAttendance hook → attendanceService → Axios
    ↓
Backend: /api/attendance/ → AttendanceController → AttendanceService → AttendanceRepository → MongoDB "attendance"
```

### Files

| Layer | File |
|-------|------|
| Controller | `apps/attendance/controllers/attendance_controller.py` |
| Service | `apps/attendance/services/attendance_service.py` |
| Repository | `apps/attendance/repositories/attendance_repository.py` |
| Serializer | `apps/attendance/serializers/attendance_serializer.py` |
| Validator | `apps/attendance/validators/attendance_validator.py` |
| Frontend page | `frontend/src/pages/attendance/AttendancePage.tsx` |
| Frontend service | `frontend/src/services/attendance.service.ts` |
| Frontend hook | `frontend/src/hooks/useAttendance.ts` |

### Business Rules

- All roles can mark/check-in/check-out.
- Employees can only view their own attendance.
- Managers can view and update any employee's attendance.
- The controller has `AttendanceController` (CRUD) and `AttendanceSummaryController` (summary stats).

---

## 14. Leave Management

### Purpose

Handles leave applications — employees apply, managers approve or reject.

### Flow

```
Frontend: LeavesPage → useLeaves hook → leaveService → Axios
    ↓
Backend: /api/leaves/ → LeaveController → LeaveService → LeaveRepository → MongoDB "leaves"
```

### Files

| Layer | File |
|-------|------|
| Controller | `apps/leave/controllers/leave_controller.py` |
| Service | `apps/leave/services/leave_service.py` |
| Repository | `apps/leave/repositories/leave_repository.py` |
| Serializer | `apps/leave/serializers/leave_serializer.py` |
| Validator | `apps/leave/validators/leave_validator.py` |
| Frontend page | `frontend/src/pages/leaves/LeavesPage.tsx` |
| Frontend service | `frontend/src/services/leave.service.ts` |
| Frontend hook | `frontend/src/hooks/useLeaves.ts` |

### Business Rules

- All roles can apply for leave.
- Employees can only view their own leaves.
- Only `HR_MANAGER`, `ADMIN`, and `SUPER_ADMIN` can approve or reject leaves.
- A user cannot approve/reject their own leave (enforced in the service layer).
- Leave records are **never deleted** — they are historical business data.

---

## 15. Payment System — Cashfree Sandbox

### IMPORTANT

EmpSphere uses **Cashfree** for payments. The system runs in **SANDBOX** mode by default. Sandbox transactions do **NOT** move real money. They are for development and testing only.

### Payment Flow

```
User opens Payments page
    ↓
Clicks "Make Payment"
    ↓
Selects "Myself" or "Select Employee"
    ↓  (SUPER_ADMIN must select an employee; others pay for themselves by default)
Selects an Amenity
    ↓
Backend supplies the amount (from amenity config, NOT from frontend)
    ↓
Backend creates a Cashfree Sandbox order
    ↓
Returns payment_session_id to frontend
    ↓
Frontend opens Cashfree Checkout (sandbox.cashfree.com)
    ↓
User completes test payment (UPI / Card / Netbanking)
    ↓
Cashfree redirects to backend callback URL
    ↓
Cashfree sends webhook to backend
    ↓
Backend verifies and updates payment status
    ↓
Payment status stored in MongoDB
    ↓
User sees updated payment history
```

### Amenities

Amenities are office items/services that employees can pay for (e.g., ID card, T-shirt, training material). Each amenity has a **name** and an **amount**.

- Amenities are configured on the **backend** (via admin panel or seed command).
- The **frontend must never determine the payment amount**. The amount always comes from the backend amenity configuration.
- Seed command: `python manage.py seed_amenities` creates test amenities with small amounts (₹5–₹20).

### Roles and Payments

| Role | Can pay for | Can view |
|------|------------|----------|
| EMPLOYEE | Themselves only | Own payments only |
| HR_MANAGER | Themselves or select employee | All payments |
| ADMIN | Themselves or select employee | All payments |
| SUPER_ADMIN | Must select an employee | All payments |

### Security

- `CASHFREE_SECRET_KEY` is **backend-only**. It never appears in frontend code, README, or logs.
- The payment amount comes from the backend amenity configuration — the frontend cannot manipulate it.
- Payment verification exists: the backend checks the actual Cashfree payment status before marking a payment as PAID.
- Webhook handling exists: Cashfree sends payment events to `/api/payment/webhook/` with signature verification.
- Duplicate/idempotency protection: if a pending payment already exists for the same employee + amenity, the existing one is reused.

### Cashfree Sandbox Configuration

Configured in `backend/.env`:

```
CASHFREE_APP_ID=YOUR_VALUE_HERE
CASHFREE_SECRET_KEY=YOUR_VALUE_HERE
CASHFREE_ENVIRONMENT=SANDBOX
CASHFREE_API_VERSION=2025-01-01
```

- `CASHFREE_ENVIRONMENT=SANDBOX` uses `https://sandbox.cashfree.com/pg`
- `CASHFREE_ENVIRONMENT=PRODUCTION` uses `https://api.cashfree.com/pg`

### Files

| Layer | File |
|-------|------|
| Gateway | `apps/payment/gateways/cashfree_gateway.py` |
| Controller | `apps/payment/controllers/payment_controller.py` |
| Webhook controller | `apps/payment/controllers/webhook_controller.py` |
| Callback controller | `apps/payment/controllers/callback_controller.py` |
| Service | `apps/payment/services/payment_service.py` |
| Repository | `apps/payment/repositories/payment_repository.py` |
| Serializer | `apps/payment/serializers/payment_serializer.py` |
| Validator | `apps/payment/validators/payment_validator.py` |
| Amenity controller | `apps/payment/amenities/amenity_controller.py` |
| Amenity service | `apps/payment/amenities/amenity_service.py` |
| Amenity repository | `apps/payment/amenities/amenity_repository.py` |
| Frontend page | `frontend/src/pages/payments/PaymentsPage.tsx` |
| Frontend service | `frontend/src/services/payment.service.ts` |
| Frontend hook | `frontend/src/hooks/usePayment.ts` |
| Seed command | `apps/common/management/commands/seed_amenities.py` |

---

## 16. Activity Logs

### Purpose

Records every important action in the system for audit purposes. Every service call to `self.log_activity(...)` writes an entry.

### Log Entry Fields

- `module` — Which module (e.g., AUTHENTICATION, PAYMENT, EMPLOYEE)
- `action` — What happened (e.g., LOGIN, PAYMENT_CREATED, EMPLOYEE_UPDATED)
- `performed_by` — User ID who performed the action
- `target_id` — The affected resource ID
- `status` — SUCCESS or FAILED
- `description` — Human-readable description
- `metadata` — Additional JSON data
- `created_at` — Timestamp

### Access Rules

- **EMPLOYEE** — Can view only their own logs.
- **HR_MANAGER / ADMIN** — Can view logs of users they manage.
- **SUPER_ADMIN** — Can view all logs.

### Files

| Layer | File |
|-------|------|
| Controller | `apps/activity_logs/views/activity_log_view.py` |
| Service | `apps/activity_logs/services/audit_service.py` |
| Frontend page | `frontend/src/pages/activityLogs/ActivityLogsPage.tsx` |
| Frontend service | `frontend/src/services/activityLog.service.ts` |

---

## 17. Reports

### Purpose

Generates management reports for employees, attendance, leaves, departments, designations, and activity logs.

### Access

Restricted to `SUPER_ADMIN`, `ADMIN`, and `HR_MANAGER`.

### Report Types

- **Employees** — Filterable by department, designation, status, joining date.
- **Attendance** — Filterable by employee, department, date range, status.
- **Leaves** — Filterable by employee, department, date range, status, leave type.
- **Departments** — With search and include-inactive filter.
- **Designations** — With search and include-inactive filter.
- **Activity** — Filterable by module, action, user, date range.

### Files

| Layer | File |
|-------|------|
| Controller | `apps/reports/controllers/report_controller.py` |
| Service | `apps/reports/services/report_service.py` |
| Repository | `apps/reports/repositories/report_repository.py` |
| Frontend page | `frontend/src/pages/reports/ReportsPage.tsx` |
| Frontend service | `frontend/src/services/report.service.ts` |

---

## 18. Statistics / Dashboard

### Purpose

Provides summary statistics for role-specific dashboards.

### Files

| Layer | File |
|-------|------|
| Controller | `apps/statistics/controllers/statistics_controller.py` |
| Service | `apps/statistics/services/statistics_service.py` |
| Frontend pages | `frontend/src/pages/dashboard/*.tsx` (4 role-specific dashboards) |
| Frontend service | `frontend/src/services/statistics.service.ts` |

### Dashboard Pages

- `SuperAdminDashboardPage.tsx`
- `AdminDashboardPage.tsx`
- `HRDashboardPage.tsx`
- `EmployeeDashboardPage.tsx`

Each dashboard shows role-relevant statistics fetched from `/api/statistics/`.

---

## 19. Environment Variables

### Backend (`backend/.env`)

```
# Django
SECRET_KEY=YOUR_VALUE_HERE
DEBUG=True

# MongoDB
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=empsphere_db

# JWT
JWT_SECRET=YOUR_VALUE_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXP_MINUTES=30
REFRESH_TOKEN_EXP_DAYS=7
PASSWORD_RESET_TOKEN_EXP_MINUTES=10

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=YOUR_VALUE_HERE
EMAIL_HOST_PASSWORD=YOUR_VALUE_HERE
DEFAULT_FROM_EMAIL=YOUR_VALUE_HERE

# Google OAuth (optional)
GOOGLE_CLIENT_ID=YOUR_VALUE_HERE
GOOGLE_CLIENT_SECRET=YOUR_VALUE_HERE

# Cashfree Sandbox
CASHFREE_APP_ID=YOUR_VALUE_HERE
CASHFREE_SECRET_KEY=YOUR_VALUE_HERE
CASHFREE_ENVIRONMENT=SANDBOX
CASHFREE_API_VERSION=2025-01-01

# Registration
COMPANY_REGISTRATION_SECRET=YOUR_VALUE_HERE

# Seed defaults
SUPER_ADMIN_EMAIL=admin@empsphere.com
SUPER_ADMIN_PASSWORD=YOUR_VALUE_HERE
SUPER_ADMIN_EMPLOYEE_CODE=EMP001

# CORS / URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ALLOWED_HOSTS=*
```

### Frontend (`frontend/.env`)

```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_APP_URL=http://localhost:3000
VITE_GOOGLE_CLIENT_ID=
```

---

## 20. Running the Project

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB running locally (or a MongoDB URI)

### Backend

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Variables section)
# Copy the variables above into backend/.env with your real values

# Seed RBAC data (roles, permissions, super admin user)
.\venv\Scripts\python.exe manage.py seed_rbac

# Seed test amenities
.\venv\Scripts\python.exe manage.py seed_amenities

# Start the server
.\venv\Scripts\python.exe manageserver
```

Backend runs at `http://localhost:8000`.

### Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Copy .env.example to .env and fill in values
Copy-Item .env.example .env

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## 21. Cashfree Sandbox Setup

1. Create a free Cashfree account at [https://www.cashfree.com](https://www.cashfree.com).
2. Go to the Cashfree Dashboard → **Sandbox** → **API Credentials**.
3. Copy the **App ID** and **Secret Key**.
4. Put them in `backend/.env`:
   ```
   CASHFREE_APP_ID=YOUR_VALUE_HERE
   CASHFREE_SECRET_KEY=YOUR_VALUE_HERE
   CASHFREE_ENVIRONMENT=SANDBOX
   ```
5. Start the backend and frontend.
6. Log in to EmpSphere.
7. Go to **Payments** → **Make Payment**.
8. Select **Myself** or an employee.
9. Select an amenity.
10. Confirm the amount (supplied by the backend).
11. The Cashfree Sandbox checkout opens.
12. Complete a test payment using Sandbox test credentials.
13. The payment status updates in Payment History.

> **SANDBOX = TESTING.** It does not move real money.

---

## 22. Debugging Guide

### 400 Bad Request

- Check the request body matches the serializer fields.
- Check backend serializer validation errors in the response.
- Check backend logs (`backend/logs/app.log` or terminal).
- For payments: check the Cashfree response and environment variables.

### 401 Unauthorized

- Check the JWT token is being sent (`Authorization: Bearer <token>`).
- Check the token is not expired.
- Check the user is logged in (Redux auth state).
- Check the `JWT_SECRET` matches between token creation and validation.

### 403 Forbidden

- Check the user's role against the `@require_role` decorator on the endpoint.
- Check resource ownership (employees can only access their own data).
- Check the `RolePermission` hierarchy.

### 404 Not Found

- Check the frontend URL matches the Django URL configuration.
- Check the API endpoint path.
- Check route parameters (e.g., `/api/employees/<id>/`).

### 500 Internal Server Error

- Check the Django terminal first — it shows the full traceback.
- Check `backend/logs/app.log`.

### CORS Errors

- Check `FRONTEND_URL` in `backend/.env` matches the frontend origin.
- Check `CORS_ALLOWED_ORIGINS` in `config/settings.py`.

### MongoDB Errors

- Check MongoDB is running (`mongod`).
- Check `MONGO_URI` in `backend/.env`.
- Check the database name.

### Cashfree Errors

- Check `CASHFREE_APP_ID` and `CASHFREE_SECRET_KEY` in `backend/.env`.
- Check `CASHFREE_ENVIRONMENT` is `SANDBOX` for testing.
- Check backend logs for the Cashfree response.
- Check the checkout configuration (return_url, notify_url).
- Check webhook signature verification.

### Frontend TypeScript

```powershell
cd frontend
npx tsc --noEmit
```

### Vite Build

```powershell
cd frontend
npm run build
```

### Browser DevTools

- **Console** — JavaScript errors, Redux logs.
- **Network** — Request/response inspection, status codes, payloads.

---

## 23. Verification

Run these commands to verify the project is healthy:

### Backend

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
```

### Frontend

```powershell
cd frontend
npx tsc --noEmit
npm run build
```

---

## 24. Deployment

### Frontend — Vercel

- Build command: `npm run build`
- Output directory: `dist`
- Environment variables: Set `VITE_API_BASE_URL` to your production backend URL.

### Backend

- Set `DEBUG=False` in production.
- Set `ALLOWED_HOSTS` to your domain.
- Set `FRONTEND_URL` to your production frontend URL.
- Set `BACKEND_URL` to your production backend URL.
- Set `CASHFREE_ENVIRONMENT=PRODUCTION` for live payments.
- Use a production MongoDB instance (e.g., MongoDB Atlas).

### Environments

| Environment | Cashfree | Purpose |
|------------|----------|---------|
| LOCAL | SANDBOX | Development on your machine |
| SANDBOX | SANDBOX | Testing with fake money |
| PRODUCTION | PRODUCTION | Live with real money |

---

## 25. Safe Future Development

When adding a new feature, follow the existing layered pattern:

```
New Feature
    ↓
Create/modify model/schema/document structure (if needed)
    ↓
Repository (database access)
    ↓
Service (business logic)
    ↓
Serializer/Validator (input validation)
    ↓
Controller (HTTP handling)
    ↓
URL (route definition)
    ↓
Frontend service (API calls)
    ↓
Hook/state (Redux slice)
    ↓
Page/component (UI)
    ↓
Testing
```

### Rules

- **Do not** put database queries directly in React components.
- **Do not** put business logic inside controllers — use the service layer.
- **Do not** expose secrets (`JWT_SECRET`, `CASHFREE_SECRET_KEY`) in frontend code.
- **Do not** trust frontend amounts or roles — always validate on the backend.
- **Do not** bypass backend authorization — always use `@require_role`.
- **Do** reuse existing services, components, and patterns.
- **Do** follow existing naming conventions.
- **Do** run verification (`python manage.py check`, `npx tsc --noEmit`, `npm run build`) before committing.

---

## 26. Fresher Learning Path

Study the project in this order:

1. **Project structure** — Understand the folder layout (this guide, Section 4).
2. **React basics** — `frontend/src/App.tsx`, `main.tsx`.
3. **TypeScript** — `frontend/src/types/`, `frontend/src/types/payment.ts`.
4. **Axios** — `frontend/src/config/axios.ts`, `frontend/src/services/api.ts`.
5. **Django** — `backend/config/settings.py`, `backend/config/urls.py`.
6. **Django REST Framework** — `backend/apps/employee/controllers/employee_controller.py`.
7. **MongoDB** — `backend/apps/common/database/mongo.py`, `backend/apps/common/core/collections.py`.
8. **Controller → Service → Repository** — Trace a request through `employee/` or `attendance/`.
9. **JWT** — `backend/apps/common/middleware/authentication.py`, `backend/apps/authentication/services/auth_service.py`.
10. **RBAC** — `backend/apps/common/core/roles.py`, `backend/apps/common/core/permissions.py`, `backend/apps/common/decorators/permission.py`.
11. **Employee module** — `backend/apps/employee/`, `frontend/src/pages/employees/`.
12. **Organization** — `backend/apps/organization/`, `frontend/src/pages/departments/`.
13. **Attendance** — `backend/apps/attendance/`, `frontend/src/pages/attendance/`.
14. **Leave** — `backend/apps/leave/`, `frontend/src/pages/leaves/`.
15. **Payment / Cashfree** — `backend/apps/payment/`, `frontend/src/pages/payments/`.
16. **Reports / Statistics** — `backend/apps/reports/`, `backend/apps/statistics/`.
17. **Deployment** — This guide, Section 24.

---

## 27. How EmpSphere Works (Summary)

### Main Flow

```
USER
    ↓
REACT FRONTEND (Vite + TypeScript)
    ↓
AXIOS (HTTP client with JWT interceptor)
    ↓
DJANGO REST API (URL routing)
    ↓
CONTROLLER (handles HTTP, extracts data)
    ↓
SERIALIZER / VALIDATOR (validates request data)
    ↓
SERVICE (business logic and rules)
    ↓
REPOSITORY (database access)
    ↓
MONGODB (data storage)
```

### Payment Flow

```
USER
    ↓
PAYMENTS PAGE (PaymentsPage.tsx)
    ↓
Select "Myself" or "Select Employee"
    ↓
Select an Amenity
    ↓
BACKEND looks up the amenity amount (never trusts frontend)
    ↓
BACKEND creates a Cashfree Sandbox order
    ↓
CASHFREE SANDBOX CHECKOUT opens in the browser
    ↓
User completes a test payment (UPI / Card / Netbanking)
    ↓
CASHFREE sends webhook to backend + redirects to callback
    ↓
BACKEND verifies payment status with Cashfree
    ↓
Payment status stored in MongoDB ("payments" collection)
    ↓
Activity log written ("payments" collection)
    ↓
User sees updated Payment History
```

### In Simple Terms

1. The **user** interacts with the React frontend (buttons, forms, tables).
2. **Axios** sends the user's request to the Django backend, attaching the JWT token.
3. The **Django URL router** directs the request to the correct **controller**.
4. The **controller** uses a **serializer** to validate the incoming data.
5. The **service** performs the actual business logic (the "brain" of the operation).
6. The **repository** talks to **MongoDB** to store or retrieve data.
7. The response flows back through the same layers to the frontend.
8. **Redux** updates the application state, and **React re-renders** the UI.

This layered approach keeps each part of the system focused on one responsibility, making the code easier to understand, test, and modify.