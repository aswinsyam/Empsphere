# EmpSphere — Project Guide

> **Purpose:** This is the single source of truth for understanding the EmpSphere backend and frontend.
> If you are new to the project, read this first.
>
> **Last updated:** After Phase 2 implementation fixes.

---

## 1. Project Overview

EmpSphere is an employee management system (HRMS) with:
- **Backend:** Django + Django REST Framework + MongoDB (PyMongo)
- **Frontend:** React + TypeScript + Vite + Axios + Redux Toolkit + Tailwind CSS

The backend exposes a REST API consumed by the React frontend.

---

## 2. Technology Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 |
| API | Django REST Framework (DRF) |
| Database | MongoDB (via PyMongo) |
| Auth | JWT (access + refresh tokens) |
| Email | Django SMTP backend (Mailpit in dev) |
| Google Auth | `google-auth` library |
| Password hashing | `passlib` + `bcrypt` |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 18 |
| Language | TypeScript |
| Bundler | Vite |
| HTTP | Axios |
| State | Redux Toolkit |
| Router | React Router |
| Styling | Tailwind CSS |
| Toasts | react-toastify |

---

## 3. Backend Folder Structure

```
backend/
├── apps/
│   ├── authentication/          # Login, register, OTP, password, profile, Google auth
│   │   ├── views/               # HTTP endpoints
│   │   ├── services/            # Business logic
│   │   ├── serializers/         # DRF request/response validation
│   │   ├── repositories/        # MongoDB data access
│   │   ├── schemas/             # MongoDB document helpers
│   │   ├── dtos/                # Data transfer objects
│   │   ├── managers/            # Small utilities (token blacklist, employee code)
│   │   ├── tests/               # Tests
│   │   ├── urls.py              # Auth URL routes
│   │   └── apps.py              # Django app config
│   │
│   ├── organization/            # Department management
│   │   ├── controllers/         # HTTP endpoints (RBAC-protected)
│   │   ├── services/            # Business logic
│   │   ├── serializers/         # DRF validation
│   │   ├── repositories/        # MongoDB data access
│   │   ├── dtos/                # Data transfer objects
│   │   ├── validators/          # Reusable validation rules
│   │   ├── urls.py              # Organization URL routes
│   │   └── apps.py
│   │
│   └── activity_logs/           # Audit / activity logging
│       ├── services/            # Write audit records
│       ├── views/               # HTTP endpoint (manual log ingestion)
│       └── apps.py
│
├── common/                      # Shared infrastructure used by all apps
│   ├── database/                # MongoDB connection (PyMongo singleton)
│   ├── security/                # Password hashing, Google OAuth
│   ├── middleware/              # DRF auth middleware, logging, exception handling
│   ├── permissions/             # DRF permission classes + RBAC helpers
│   ├── decorators/              # `@require_role` decorator
│   ├── responses/               # Standardized API response format
│   ├── exceptions/              # Custom exceptions + DRF exception handler
│   ├── base/                    # Base classes for Service, Controller, Manager
│   ├── core/                    # Constants: roles, collections, status codes
│   ├── config/                  # App configuration (environment variables)
│   └── logging/                 # Audit logger
│
├── config/                      # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .env
└── templates/
    └── emails/
        └── otp_email.html        # OTP email HTML template
```

---

## 4. Frontend Folder Structure

```
frontend/src/
├── App.tsx                      # Root component (Redux + Router + ToastProvider)
├── main.tsx                     # Entry point
├── config/
│   ├── axios.ts                 # Axios instance with JWT interceptors
│   └── env.ts                   # Environment variables
├── hooks/
│   ├── useAuth.ts               # Auth state hook
│   └── useDepartments.ts        # Departments hook
├── services/
│   ├── api.ts                   # Generic HTTP wrapper
│   ├── auth.service.ts          # Auth API calls
│   ├── department.service.ts    # Department API calls
│   └── user.service.ts          # User API calls
├── store/
│   ├── index.ts                 # Redux store
│   ├── middleware/
│   │   └── authMiddleware.ts    # Auth middleware
│   └── slices/
│       ├── authSlice.ts         # Auth state
│       ├── departmentSlice.ts   # Department state
│       └── userSlice.ts         # User state
├── components/
│   ├── auth/                    # Auth forms (Login, Register, OTP, Password)
│   ├── common/                  # Shared UI (Avatar, Button, Input, ToastProvider)
│   ├── dashboard/               # Dashboard content
│   ├── layout/                  # Navbar, Sidebar, DashboardLayout
│   └── users/                   # Create user form
├── pages/
│   ├── auth/                    # Auth pages
│   ├── dashboard/               # Role-based dashboards
│   ├── departments/             # Departments page
│   ├── errors/                  # 404, 401 pages
│   ├── profile/                 # Profile page
│   └── users/                   # Create user page
├── routes/
│   ├── AppRoutes.tsx            # Route definitions
│   ├── ProtectedRoute.tsx       # Auth guard
│   ├── RequireRole.tsx          # RBAC guard
│   └── DashboardRedirect.tsx    # Role-based redirect
├── types/
│   ├── api.ts                   # Generic API response types
│   ├── auth.ts                  # Auth payload/result types
│   ├── department.ts            # Department types
│   └── user.ts                  # User types
├── utils/
│   ├── constants.ts             # App constants (routes, etc.)
│   ├── helpers.ts               # Utility functions
│   └── token.ts                 # JWT token storage helpers
└── styles/
    └── globals.css              # Global styles + Tailwind
```

---

## 5. Backend Architecture

```
HTTP Request
    ↓
Django URL Router (config/urls.py)
    ↓
App URL Router (apps/*/urls.py)
    ↓
View (APIView)
    ↓
Serializer (DRF validation)
    ↓
Service (business logic)
    ↓
Repository (MongoDB access)
    ↓
PyMongo / MongoDB
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| **View** | Receives HTTP request, calls serializer/service, returns response |
| **Serializer** | Validates request data, serializes response data |
| **Service** | Contains business logic, coordinates repositories |
| **Repository** | Encapsulates all PyMongo/MongoDB operations |
| **Schema** | Low-level MongoDB document helpers |

**Important:** No Django ORM models are used. All data is stored in MongoDB documents accessed via PyMongo.

---

## 6. Frontend Architecture

```
React Component
    ↓
Service (auth.service.ts, user.service.ts, etc.)
    ↓
API client (src/services/api.ts → http.get/post/patch/delete)
    ↓
Axios instance (src/config/axios.ts)
    ↓
Django REST API
```

### State Management

```
Component
    ↓
useAuth hook (or useDispatch)
    ↓
Redux Toolkit slice (authSlice.ts)
    ↓
Service → API → Backend
```

---

## 7. Authentication System

### Register
1. Frontend: `RegisterForm` → `authService.register()`
2. Backend: `AuthView` → `AuthSerializer` → `AuthService.register()`
3. Creates user document with `is_email_verified=False`
4. Returns `user_id`
5. Frontend navigates to OTP verification page

### Login
1. Frontend: `LoginForm` → `authService.login()`
2. Backend: `AuthView` → `AuthSerializer` → `AuthService.login()`
3. Verifies email/password
4. If email not verified → sends OTP, returns `requires_otp: true`
5. If verified → generates access + refresh JWT

### Logout
1. Frontend: `useAuth.logout()` → `authService.logout()`
2. Backend: `AuthView._logout()` → blacklists refresh token in memory
3. Frontend clears stored tokens

### Refresh Token
1. Frontend: Axios interceptor catches 401 → calls refresh endpoint
2. Backend: `RefreshTokenView` → `AuthService.refresh_token()`
3. Validates refresh token, blacklists old one, issues new pair

### Get Current User (Me)
1. Frontend: `useAuth` → `userService.getMe()`
2. Backend: `UserView.get()` → `UserService.get_by_id()`
3. Returns user document

### Email Verification (OTP)
1. Frontend: `VerifyEmailForm` → `authService.sendOtp()` / `authService.verifyOtp()`
2. Backend: `OTPView` → `OTPService.send_otp()` / `OTPService.verify_otp()`
3. OTP stored in MongoDB with 10-minute expiry
4. Email sent via Django SMTP

### Google Login
1. Frontend: `GoogleAuthButton` → `authService.googleLogin()`
2. Backend: `GoogleLoginView` → `AuthService.google_login()`
3. Verifies Google ID token, finds/creates user, generates JWT

### Change Password
1. Frontend: `ChangePasswordForm` → `userService.changePassword()`
2. Backend: `PasswordView._change_password()` → `PasswordService.change_password()`
3. Verifies current password, updates hash

### Forgot Password
1. Frontend: `ForgotPasswordForm` → `authService.forgotPassword()`
2. Backend: `PasswordView._forgot_password()` → `OTPService.send_otp()` with `purpose="password_reset"`
3. OTP sent to user's email

### Reset Password
1. Frontend: `ResetPasswordForm` → `authService.resetPassword()`
2. Backend: `PasswordView._reset_password()` → verifies OTP → `PasswordService.set_password()`
3. Updates password without requiring old password

### Set Password (Google Users)
1. Frontend: `SetPasswordForm` → `authService.setPassword()`
2. Backend: `PasswordView._set_password()` → verifies OTP with `purpose="password_setup"` → `PasswordService.set_password()`

### Profile Update
1. Frontend: `ProfilePage` → `userService.updateProfile()`
2. Backend: `UserView.patch()` → `UserService.update()`
3. Updates user document fields

### Profile Image Upload
1. Frontend: `ProfilePage` → `userService.uploadProfileImage()`
2. Backend: `ProfileImageView.post()` → saves file to `MEDIA_ROOT/profiles/` → `UserService.update_profile_image()`
3. Returns updated user with `profile_image` URL

---

## 8. Password Flows

| Flow | Endpoint | Input | Backend Method | Purpose |
|------|----------|-------|----------------|---------|
| Change Password | `POST /api/auth/change-password/` | `current_password`, `new_password` | `PasswordService.change_password()` | Authenticated user changes own password |
| Forgot Password | `POST /api/auth/forgot-password/` | `email` | `OTPService.send_otp()` | Sends password reset OTP |
| Reset Password | `POST /api/auth/reset-password/` | `token`, `new_password`, `email` | `OTPService.verify_otp()` + `PasswordService.set_password()` | Resets password via OTP |
| Set Password | `POST /api/auth/set-password/` | `otp`, `new_password`, `email` | `OTPService.verify_otp()` + `PasswordService.set_password()` | Google users set local password |

---

## 9. OTP Architecture

### Files

| File | Purpose |
|------|---------|
| `views/otp_view.py` | HTTP endpoint, dispatches send/verify by `purpose` |
| `services/otp_service.py` | OTP generation, storage, verification, expiration, email delivery |
| `repositories/otp_repository.py` | MongoDB collection operations for OTPs |
| `serializers/otp_serializer.py` | DRF validation for OTP payloads |
| `dtos/otp_dto.py` | Data transfer objects (used by tests) |

### Flow

```
OTPView.post()
    ↓
OTPService.send_otp() / verify_otp()
    ↓
OTPRepository (invalidate_active / create / get_active / mark_used)
    ↓
MongoDB (otps collection)
```

### Email Delivery

`OTPService.send_otp()` now calls `_send_otp_email()` which:
1. Renders `templates/emails/otp_email.html`
2. Sends via Django `send_mail()` using SMTP settings

---

## 10. MongoDB Architecture

### Connection
- **File:** `apps/common/database/mongo.py`
- **Type:** Singleton `MongoConnection` using `pymongo.MongoClient`
- **Config:** `apps/common/config/settings.py` reads `MONGO_URI` and `DATABASE_NAME` from `.env`

### Collections
Defined in `apps/common/core/collections.py`:
- `USERS`
- `OTPS`
- `DEPARTMENTS`
- `ACTIVITY_LOGS`
- `SEQUENCES`

### Document Pattern
- `_id` fields are MongoDB `ObjectId`s
- Repositories convert string IDs to `ObjectId` for queries
- Repositories return string IDs for created documents

---

## 11. RBAC (Role-Based Access Control)

### Roles
| Role | Value | Description |
|------|-------|-------------|
| `EMPLOYEE` | 1 | Base access |
| `HR_MANAGER` | 2 | Can manage employees |
| `ADMIN` | 3 | Can manage HR + employees |
| `SUPER_ADMIN` | 4 | Full access |

### How RBAC Works
- `RolePermission` in `common/permissions/role_permission.py` provides helpers
- `@require_role(*roles)` decorator checks the authenticated user's role
- `MANAGABLE_ROLES` defines who can create/update which roles

### Department RBAC
| Operation | Who Can Access |
|-----------|----------------|
| List | HR_MANAGER, ADMIN, SUPER_ADMIN |
| Create | ADMIN, SUPER_ADMIN |
| Detail | HR_MANAGER, ADMIN, SUPER_ADMIN |
| Update | ADMIN, SUPER_ADMIN |
| Delete | SUPER_ADMIN only |

---

## 12. Frontend State Management

### Redux Toolkit
- **Store:** `src/store/index.ts`
- **Auth slice:** `src/store/slices/authSlice.ts`
  - Manages `user`, `loading`, `initializing`, `error`
  - Async thunks: `login`, `register`, `fetchMe`, `logoutUser`, `googleLogin`
- **useAuth hook:** `src/hooks/useAuth.ts` — convenient access to auth state and actions

### Axios
- **Instance:** `src/config/axios.ts`
- **Features:**
  - Attaches Bearer access token to every request
  - On 401, attempts token refresh once before retrying
  - On refresh failure, dispatches `auth:expired` event
  - No circular dependency with auth service

### Toast Notifications
- **Provider:** `src/components/common/ToastProvider.tsx` — mounted at app root
- **Utilities:** `toastSuccess()`, `toastError()`, `withToast()`, `showApiError()`
- **Usage:** Auth forms, profile page, password forms call toasts for user feedback

---

## 13. SMTP / Mailpit

### Configuration
- **Backend:** `django.core.mail.backends.smtp.EmailBackend`
- **Defaults:** `localhost:25`, no TLS
- **Settings in:** `config/settings.py`

### Email Flow
```
OTPService.send_otp()
    ↓
render_to_string("emails/otp_email.html")
    ↓
send_mail() via Django SMTP
    ↓
Mailpit (dev) / real SMTP (prod)
```

### Template
- **File:** `templates/emails/otp_email.html`
- **Variables:** `{{ otp }}`, `{{ year }}`, `{{ purpose }}`

---

## 14. API Endpoint Table

| Method | Endpoint | View | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/register/` | `AuthView` | Register new user |
| POST | `/api/auth/login/` | `AuthView` | Login with email/password |
| POST | `/api/auth/logout/` | `AuthView` | Logout (blacklist refresh token) |
| POST | `/api/auth/refresh-token/` | `RefreshTokenView` | Get new access token |
| GET | `/api/auth/me/` | `UserView` | Get current user |
| GET/PATCH | `/api/auth/profile/` | `UserView` | Get/update profile |
| POST | `/api/auth/profile/image/` | `ProfileImageView` | Upload profile image |
| POST | `/api/auth/users/create/` | `UserView` | Create user (admin) |
| POST | `/api/auth/verify-email/` | `VerifyEmailView` | Verify email via OTP |
| POST | `/api/auth/google-login/` | `GoogleLoginView` | Google OAuth login |
| POST | `/api/auth/send-otp/` | `OTPView` | Send OTP |
| POST | `/api/auth/verify-otp/` | `OTPView` | Verify OTP |
| POST | `/api/auth/change-password/` | `PasswordView` | Change password |
| POST | `/api/auth/forgot-password/` | `PasswordView` | Request password reset OTP |
| POST | `/api/auth/reset-password/` | `PasswordView` | Reset password via OTP |
| POST | `/api/auth/set-password/` | `PasswordView` | Set password (Google users) |
| GET | `/api/organization/departments/` | `DepartmentController` | List departments |
| POST | `/api/organization/departments/` | `DepartmentController` | Create department |
| GET | `/api/organization/departments/<id>/` | `DepartmentController` | Department detail |
| PUT | `/api/organization/departments/<id>/` | `DepartmentController` | Update department |
| DELETE | `/api/organization/departments/<id>/` | `DepartmentController` | Delete department |

---

## 15. Environment Variables

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=empsphere_db
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXP_MINUTES=30
REFRESH_TOKEN_EXP_DAYS=7
EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000
COMPANY_REGISTRATION_SECRET=your-company-secret
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## 16. "Where do I edit?"

| Want to change... | Edit these files |
|-------------------|------------------|
| Login | `backend/apps/authentication/services/auth_service.py`, `frontend/src/components/auth/LoginForm.tsx` |
| Register | `backend/apps/authentication/services/auth_service.py`, `frontend/src/components/auth/RegisterForm.tsx` |
| OTP | `backend/apps/authentication/services/otp_service.py`, `backend/apps/authentication/repositories/otp_repository.py`, `backend/apps/authentication/serializers/otp_serializer.py` |
| Email template | `backend/templates/emails/otp_email.html` |
| Departments | `backend/apps/organization/controllers/department_controller.py`, `backend/apps/organization/services/department_service.py`, `backend/apps/organization/repositories/department_repository.py` |
| Profile | `backend/apps/authentication/services/user_service.py`, `backend/apps/authentication/repositories/user_repository.py`, `frontend/src/pages/profile/ProfilePage.tsx` |
| Password | `backend/apps/authentication/services/password_service.py`, `backend/apps/authentication/views/password_view.py` |
| JWT | `backend/apps/authentication/services/auth_service.py` (token generation), `backend/apps/common/middleware/authentication.py` (token validation) |
| MongoDB | `backend/apps/common/database/mongo.py`, `backend/apps/common/config/settings.py` |
| SMTP | `backend/config/settings.py` (email configuration) |
| API configuration | `frontend/src/config/axios.ts`, `frontend/src/config/env.ts` |
| Redux auth state | `frontend/src/store/slices/authSlice.ts` |
| RBAC | `backend/apps/common/permissions/role_permission.py`, `backend/apps/common/decorators/permission.py` |

---

## 17. Troubleshooting

| Problem | Solution |
|---------|----------|
| MongoDB unavailable | Start MongoDB: `mongod` or `docker run -d -p 27017:27017 mongo` |
| SMTP/Mailpit unavailable | OTP emails will fail silently; check `logs/app.log` |
| 401 Unauthorized | Access token expired or invalid; check token in localStorage |
| 403 Forbidden | User role lacks permission; check role in Redux state |
| OTP invalid/expired | OTP expires after 10 minutes; request a new one |
| JWT expired | Use refresh token or log in again |
| Google OAuth failure | Check `GOOGLE_CLIENT_ID` and `GOOGLE_REDIRECT_URI` in `.env` |
| Frontend build error | Run `npm run build` to see TypeScript errors |
| CORS error | Backend allows `http://localhost:3000` and `http://127.0.0.1:3000` |
| Profile image not showing | Ensure `MEDIA_URL` and `MEDIA_ROOT` are served in development |

---

## 18. Files Removed During Cleanup

| File(s) | Reason |
|---------|--------|
| `authentication/controllers/*` | Dead code. Not wired in `urls.py`. Duplicated views. |
| `authentication/dtos/auth_dto.py`, `password_dto.py`, `user_dto.py` | Only used by dead controllers. |
| `authentication/managers/otp_manager.py` | Duplicated OTP logic already in `OTPService`. |
| `authentication/managers/email_manager.py` | Dead code. Not used by any active service. |
| `authentication/validators/*` | Dead code. Not imported by any active view or serializer. |
| `organization/schemas/department_schema.py` | Dead code. Caused double-insert bug. Logic moved to repository. |
| `common/base/base_repository.py` | Dead code. No active repository inherits from it. |
| `common/database/mongo_manager.py` | Dead code. Unused wrapper. |
| `common/security/jwt_manager.py` | Dead code. Views use inline `jwt.encode()`. |
| `common/email/email_service.py` | Dead code. Not imported by any active code. |
| `common/storage/file_manager.py` | Dead code. Not imported anywhere. |
| `common/utils/document_helper.py` | Dead code. Only used by dead `base_repository.py`. |
| `common/core/defaults.py` | Dead code. Only used by dead `file_manager.py`. |
| `common/core/regex.py` | Dead code. Not imported anywhere. |
| `organization/views/department_view.py` | Dead code. Not wired in `urls.py`. |
| `authentication/repositories/sequence_repository.py` | Dead code. Not imported anywhere. |

---

## 19. Remaining Issues

| Issue | Status |
|-------|--------|
| OTP email delivery | ✅ Implemented via Django SMTP |
| Profile image upload | ✅ Implemented |
| Axios circular dependency | ✅ Fixed |
| ToastProvider mounted | ✅ Mounted in App.tsx |
| Password flow consistency | ✅ Fixed (forgot/reset/set now use OTP) |
| Dead department_view.py | ✅ Removed |
| Dead sequence_repository.py | ✅ Removed |
| In-memory token blacklist | ⚠️ Known limitation (lost on restart) |
| MongoDB unavailable | ⚠️ Cannot test without running MongoDB |

---

*This guide documents the actual current state of the project. If you modify code, update this guide accordingly.*
