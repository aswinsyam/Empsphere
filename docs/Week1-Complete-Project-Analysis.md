# EmpSphere — Week 1 Complete Project Analysis

> **Beginner-Friendly Guide to the EmpSphere Authentication System**
> This document explains the entire Week 1 project — how the backend and frontend work together, what each file does, and how every authentication feature flows from the browser to the database and back.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Backend Folder Structure](#2-backend-folder-structure)
3. [Frontend Folder Structure](#3-frontend-folder-structure)
4. [Backend Architecture](#4-backend-architecture)
5. [Authentication Architecture](#5-authentication-architecture)
6. [JWT Implementation](#6-jwt-implementation)
7. [Refresh Token & Blacklist](#7-refresh-token--blacklist)
8. [OTP Implementation](#8-otp-implementation)
9. [Email Configuration](#9-email-configuration)
10. [Mailpit — How to View Emails in Development](#91-mailpit--how-to-view-emails-in-development)
11. [Company Registration Code (3456)](#92-company-registration-code-3456)
12. [Google Authentication](#10-google-authentication)
13. [RBAC & Role Hierarchy](#11-rbac--role-hierarchy)
14. [Middleware & Exception Handling](#12-middleware--exception-handling)
15. [ApiResponse](#13-apiresponse)
16. [MongoDB / PyMongo](#14-mongodb--pymongo)
17. [Frontend Routing](#15-frontend-routing)
18. [Redux Toolkit State Management](#16-redux-toolkit-state-management)
19. [Axios Configuration & Interceptors](#17-axios-configuration--interceptors)
20. [Authentication Flow (Step by Step)](#18-authentication-flow-step-by-step)
21. [Protected Routes](#19-protected-routes)
22. [Role-Based Dashboard Routing](#20-role-based-dashboard-routing)
23. [Profile Functionality](#21-profile-functionality)
24. [Change Password](#22-change-password)
25. [Forgot Password](#23-forgot-password)
26. [Reset Password](#24-reset-password)
27. [Email Verification](#25-email-verification)
28. [Google Login Flow](#26-google-login-flow)
29. [Important File Explanations](#27-important-file-explanations)
30. [Missing Features](#28-missing-features)
31. [Partially Implemented Features](#29-partially-implemented-features)
32. [Potential Bugs](#30-potential-bugs)

---

## 1. Project Overview

**EmpSphere** is a full-stack Employee Management System built with:

- **Backend**: Django + Django REST Framework + MongoDB (via PyMongo)
- **Frontend**: React + TypeScript + Vite + Redux Toolkit + Tailwind CSS
- **Authentication**: JWT (access + refresh tokens), OTP, Google OAuth2, RBAC

The Week 1 scope focuses on **authentication and user management** — registration, login, email verification, password management, Google login, profile management, and role-based access control.

---

## 2. Backend Folder Structure

```
backend/
├── .env                          # Environment variables (secrets)
├── db.sqlite3                    # Django's default DB (used for admin only)
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── config/                       # Django project configuration
│   ├── settings.py               # Main Django settings
│   ├── urls.py                   # Root URL configuration
│   ├── asgi.py                   # ASGI entry point
│   └── wsgi.py                   # WSGI entry point
├── apps/
│   ├── authentication/           # Authentication & user management
│   │   ├── controllers/          # API endpoints (views)
│   │   ├── services/             # Business logic
│   │   ├── repositories/         # Database operations
│   │   ├── managers/             # Helper utilities (OTP, JWT, email, etc.)
│   │   ├── dtos/                 # Data transfer objects
│   │   ├── serializers/          # DRF request/response validation
│   │   ├── validators/           # Business rule validators
│   │   ├── schemas/              # MongoDB document schemas
│   │   ├── permissions.py        # DRF permission classes
│   │   └── urls.py               # Auth API routes
│   ├── common/                   # Shared infrastructure
│   │   ├── base/                 # BaseController, BaseService, BaseRepository
│   │   ├── config/               # App settings (env loading)
│   │   ├── core/                 # Constants (roles, collections, messages, regex)
│   │   ├── database/             # MongoDB connection manager
│   │   ├── decorators/           # Role-based decorators
│   │   ├── email/                # Email service & templates
│   │   ├── exceptions/           # Custom exceptions & handler
│   │   ├── logging/              # Audit logging
│   │   ├── middleware/           # JWT auth, exception, request logging
│   │   ├── permissions/          # Role permission helpers
│   │   ├── responses/            # ApiResponse builder
│   │   ├── security/             # JWT, password, Google managers
│   │   ├── storage/              # File upload manager
│   │   └── utils/                # Document helpers
│   ├── organization/             # Department management (Week 1 partial)
│   └── activity_logs/            # Audit log service
├── templates/emails/             # HTML email templates
├── logs/                         # Application log files
└── media/                        # Uploaded files (profiles, payslips, etc.)
```

---

## 3. Frontend Folder Structure

```
frontend/
├── index.html                    # HTML entry (loads Google Identity Services)
├── package.json                  # npm dependencies
├── vite.config.ts                # Vite configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── .env                          # Frontend environment variables
└── src/
    ├── main.tsx                  # React entry point
    ├── App.tsx                   # Root component (Redux + Router)
    ├── components/
    │   ├── AppBootstrap.tsx      # Session restore on app load
    │   ├── auth/                 # Login, Register, OTP, Password forms
    │   ├── common/               # Reusable UI components (Button, Input, etc.)
    │   ├── dashboard/            # Dashboard content components
    │   ├── layout/               # Sidebar, Navbar, DashboardLayout
    │   └── users/                # CreateUserForm
    ├── config/
    │   ├── axios.ts              # Axios instance with interceptors
    │   └── env.ts                # Environment variable access
    ├── hooks/
    │   ├── useAuth.ts            # Auth state hook
    │   └── useDepartments.ts     # Department state hook
    ├── pages/
    │   ├── auth/                 # Login, Register, Forgot, Reset, Verify pages
    │   ├── dashboard/            # Role-specific dashboards
    │   ├── departments/          # Department management
    │   ├── errors/               # 404, Unauthorized pages
    │   ├── profile/              # Profile page
    │   └── users/                # CreateUser page
    ├── routes/
    │   ├── AppRoutes.tsx         # Central route configuration
    │   ├── ProtectedRoute.tsx    # Auth guard
    │   ├── RequireRole.tsx       # Role guard
    │   └── DashboardRedirect.tsx # Role-based dashboard redirect
    ├── services/
    │   ├── api.ts                # Typed HTTP wrapper
    │   ├── auth.service.ts       # Auth API calls
    │   ├── user.service.ts       # User API calls
    │   └── department.service.ts # Department API calls
    ├── store/
    │   ├── index.ts              # Redux store configuration
    │   ├── middleware/           # Redux middleware
    │   └── slices/               # Redux slices (auth, user, department)
    ├── types/                    # TypeScript type definitions
    ├── utils/
    │   ├── constants.ts          # Roles, routes, nav items
    │   ├── helpers.ts            # Utility functions
    │   └── token.ts              # Token storage helpers
    └── styles/globals.css        # Global styles
```

---

## 4. Backend Architecture

The backend follows a **layered architecture**:

```
Controller → Serializer → DTO → Service → Repository → MongoDB
```

### BaseController
**File**: `backend/apps/common/base/base_controller.py`

- Provides static `success()` and `error()` methods
- Every controller inherits from it
- Returns standardized `ApiResponse` objects

### BaseService
**File**: `backend/apps/common/base/base_service.py`

- Provides `log_activity()` for audit logging
- Every service that needs audit logging inherits from it
- Uses `AuditService` to write to the `activity_logs` collection

### BaseRepository
**File**: `backend/apps/common/base/base_repository.py`

- Provides generic CRUD operations for MongoDB:
  - `create()` — insert a document
  - `get_by_id()` — find by ObjectId
  - `get_one()` — find one by filters
  - `get_all()` — find all by filters
  - `update()` — update a document
  - `soft_delete()` — mark as deleted (not physically removed)
  - `activate()` / `deactivate()` — toggle active status
  - `exists()` — check if a document exists
  - `count()` — count documents
- Automatically adds `is_deleted: False` to all queries
- Uses `DocumentHelper` for metadata (created_at, updated_at, etc.)

---

## 5. Authentication Architecture

The authentication module is organized as:

```
Controllers (API endpoints)
    ↓
Serializers (validate request data)
    ↓
DTOs (data transfer objects)
    ↓
Services (business logic)
    ↓
Repositories (MongoDB operations)
    ↓
MongoDB Collections
```

### Controllers
- `auth_controller.py` — Register, Login, Logout, Me, RefreshToken, VerifyEmail, GoogleLogin, Profile
- `otp_controller.py` — SendOTP, VerifyOTP
- `password_controller.py` — ChangePassword, ForgotPassword, ResetPassword
- `user_controller.py` — CreateUser (Admin/HR/Employee)

### Services
- `auth_service.py` — RegisterService, LoginService, LogoutService, MeService, RefreshTokenService, VerifyEmailService, GoogleLoginService, UpdateProfileService, UploadProfileImageService
- `otp_service.py` — SendOTPService, VerifyOTPService
- `password_service.py` — ChangePasswordService, ForgotPasswordService, ResetPasswordService
- `user_service.py` — CreateUserService

### Repositories
- `user_repository.py` — User-specific DB operations
- `otp_repository.py` — OTP-specific DB operations
- `sequence_repository.py` — Atomic sequence generation for employee codes

### Managers
- `jwt_manager.py` — JWT token generation/decode (wraps common JWTManager)
- `otp_manager.py` — OTP generation, hashing, verification
- `email_manager.py` — Email composition and sending
- `password_manager.py` — Password hashing/verification (wraps common PasswordManager)
- `token_blacklist_manager.py` — Refresh token blacklisting
- `employee_code_manager.py` — Employee code generation

---

## 6. JWT Implementation

### Where JWT is generated
**File**: `backend/apps/common/security/jwt_manager.py`

The `JWTManager` class creates two types of tokens:

1. **Access Token** — expires in 30 minutes
2. **Refresh Token** — expires in 7 days

### Token Payload
```python
{
    "user_id": "64f...",
    "email": "user@example.com",
    "role": "EMPLOYEE",
    "token_type": "access" | "refresh",
    "jti": "uuid4()",          # Unique token ID
    "exp": expiration_time,
    "iat": issued_at_time
}
```

### Login Flow
1. User submits email + password
2. `LoginService.login()` validates credentials
3. `JWTManager.generate_access_token(user)` creates access token
4. `JWTManager.generate_refresh_token(user)` creates refresh token
5. Both tokens are returned to the frontend
6. Frontend stores them in `localStorage`

### Protected API Authentication
**File**: `backend/apps/common/middleware/authentication.py`

- `JWTAuthentication` class is the DRF authentication backend
- Reads the `Authorization: Bearer <token>` header
- Decodes the JWT and validates `token_type == "access"`
- Loads the user from MongoDB by `user_id`
- Attaches the user dict to `request.user`

---

## 7. Refresh Token & Blacklist

### Refresh Token Rotation
**File**: `backend/apps/authentication/services/auth_service.py` → `RefreshTokenService`

When a refresh token is used:
1. Check if it's blacklisted → reject if so
2. Decode and validate the token
3. Verify `token_type == "refresh"`
4. Load the user from MongoDB
5. **Blacklist the old refresh token** (rotation)
6. Issue a **new access token** and a **new refresh token**

### Token Blacklist
**File**: `backend/apps/authentication/managers/token_blacklist_manager.py`

- Stores revoked refresh tokens in the `tokens` collection
- Uses a **unique index on `jti`** to prevent duplicates
- Uses a **TTL index on `expires_at`** so MongoDB auto-deletes expired entries
- Stores a **SHA-256 hash** of the token (never the raw token)
- `blacklist(token)` — revokes a token
- `is_blacklisted(token)` — checks if a token is revoked

### Logout
1. Frontend sends the refresh token to `/auth/logout/`
2. `LogoutService.logout()` calls `TokenBlacklistManager.blacklist()`
3. The refresh token is permanently revoked
4. Frontend clears both tokens from `localStorage`

---

## 8. OTP Implementation

### Where OTP is generated
**File**: `backend/apps/authentication/managers/otp_manager.py`

- `OTPManager.generate_otp()` — generates a 6-digit numeric OTP using `secrets.randbelow()`
- `OTPManager.create_and_send()` — generates, stores, and emails the OTP

### Where OTP is stored
- Stored in the **`otps`** MongoDB collection
- Document structure:
```python
{
    "email": "user@example.com",
    "purpose": "email_verification" | "password_reset",
    "otp_hash": "sha256_hash",     # Never stored in plaintext
    "is_used": False,
    "expires_at": datetime_utcnow + 10_minutes
}
```

### Expiry
- Default expiry: **10 minutes**
- `OTPRepository.get_active()` checks `expires_at > now` and `is_used == False`

### Verification
**File**: `backend/apps/authentication/services/otp_service.py` → `VerifyOTPService`

1. Hash the submitted OTP
2. Look up an active (unused, unexpired) OTP matching email + purpose + hash
3. If not found → raise `UnauthorizedException("Invalid or expired OTP.")`
4. If found → mark as used via `OTPRepository.mark_used()`
5. If purpose is `email_verification` → update user's `is_email_verified` to `True`

### Email Sending
- `OTPManager.create_and_send()` calls `EmailManager.send_otp_email()`
- `EmailManager` uses `EmailService.send()` with the `otp_email.html` template

### How OTP is invalidated
- **Marked as used** after successful verification (`is_used = True`)
- **Expires** after 10 minutes (`expires_at` check)
- **New OTPs** for the same email/purpose create new documents (old ones remain but are unusable)

### Which APIs use OTP
| API | Purpose |
|-----|---------|
| `POST /api/auth/send-otp/` | Send an OTP (email_verification or password_reset) |
| `POST /api/auth/verify-otp/` | Verify an OTP |

---

## 9. Email Configuration

### Email Service
**File**: `backend/apps/common/email/email_service.py`

- Uses Django's `EmailMultiAlternatives` for HTML emails
- Renders templates from `backend/templates/emails/`
- Reads SMTP settings from environment variables

### Email Templates
**File**: `backend/apps/common/email/email_templates.py`

| Template | Purpose |
|----------|---------|
| `emails/verify_email.html` | Email verification link |
| `emails/forgot_password.html` | Password reset link |
| `emails/otp_email.html` | OTP code email |
| `emails/welcome.html` | Welcome email (not yet used) |

### Email Manager
**File**: `backend/apps/authentication/managers/email_manager.py`

- `send_verification_email()` — sends a verification link
- `send_forgot_password_email()` — sends a password reset link
- `send_otp_email()` — sends an OTP code

### SMTP Settings (from `.env`)
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`

---

## 9.1 Mailpit — How to View Emails in Development

### What is Mailpit?

**Mailpit** is a free, open-source email testing tool. It acts like a **fake email server** (SMTP server) that runs on your computer. When your Django backend sends an email (like an OTP code or password reset link), Mailpit **catches** that email instead of actually sending it to a real inbox. Then you can open Mailpit's web interface in your browser to **read the email** — just like opening Gmail or Outlook.

### Why do we need Mailpit?

In development, we **do NOT want to send real emails** to real people. That would be:
- **Slow** — real SMTP servers (like Gmail) have delays
- **Risky** — we might accidentally email real users with test data
- **Impossible** — we don't have a real SMTP server configured

Mailpit solves this by pretending to be an email server. It catches every email and shows it to you in a nice web UI.

### How Mailpit Works (Simple Analogy)

```
Your Django App
      │
      │  "I want to send an email to user@example.com"
      │
      ▼
┌─────────────────┐
│   Mailpit       │  ← Mailpit catches the email (like a mailbox)
│  (SMTP Server)  │
│  Port: 1025     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mailpit Web UI │  ← You open this in your browser to read emails
│  http://localhost:8025  │
└─────────────────┘
```

### Step-by-Step: How to Use Mailpit

#### Step 1: Install Mailpit

Mailpit is a single executable file. You install it using one of these methods:

**Option A — Using Go (if you have Go installed):**
```bash
go install github.com/axllent/mailpit@latest
```

**Option B — Using Homebrew (macOS/Linux):**
```bash
brew install axllent/tap/mailpit
```

**Option C — Using Scoop (Windows):**
```bash
scoop bucket add axllent https://github.com/axllent/scoop.git
scoop install mailpit
```

**Option D — Direct Download (Windows):**
1. Go to https://github.com/axllent/mailpit/releases
2. Download the latest `mailpit-windows-amd64.zip` file
3. Extract it to a folder (e.g., `C:\mailpit`)
4. Add that folder to your system PATH

#### Step 2: Start Mailpit

Open a terminal and run:
```bash
mailpit
```

You should see output like:
```
[mailpit] 2026/08/11 09:00:00 SMTP server listening on 0.0.0.0:1025
[mailpit] 2026/08/11 09:00:00 Web UI listening on http://0.0.0.0:8025
```

This means:
- **SMTP server** is running on port **1025** (this is where Django sends emails)
- **Web UI** is running on port **8025** (this is where you read emails)

#### Step 3: Verify Your `.env` is Configured for Mailpit

Open `backend/.env` and make sure these values are set:

```env
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

**Important:** The `EMAIL_PORT=1025` is the key setting. This tells Django to send emails to Mailpit instead of a real email server.

#### Step 4: Start Your Django Backend

```bash
cd backend
python manage.py runserver 8000
```

#### Step 5: Trigger an Email

Now trigger any feature that sends an email. For example:

- **Register a new account** → no email is sent on registration
- **Send OTP** → `POST /api/auth/send-otp/` with `{ "email": "test@example.com", "purpose": "email_verification" }`
- **Forgot Password** → `POST /api/auth/forgot-password/` with `{ "email": "test@example.com" }`
- **Login with OTP** → On the login page, click the "OTP" tab, enter your email, click "Send OTP"

#### Step 6: Read the Email in Mailpit

1. Open your browser and go to: **http://localhost:8025**
2. You'll see a list of all emails Mailpit has caught
3. Click on an email to read it
4. You'll see the **OTP code** or **password reset link** inside the email body

### What You'll See in Mailpit

When you open Mailpit's web UI, you'll see:

```
┌─────────────────────────────────────────────────────┐
│  Mailpit                                             │
│  ─────────────────────────────────────────────────   │
│  From: webmaster@localhost                           │
│  To:   test@example.com                              │
│  Subject: Your verification code                     │
│  ─────────────────────────────────────────────────   │
│  Your verification code is: 482913                   │
│  This code will expire in 10 minutes.                │
└─────────────────────────────────────────────────────┘
```

### Common Mailpit Features

| Feature | How to Use |
|---------|------------|
| **View emails** | Open `http://localhost:8025` in your browser |
| **Search emails** | Use the search bar at the top of the Mailpit UI |
| **Delete emails** | Click the trash icon next to an email |
| **Delete all emails** | Click the "Delete all" button |
| **View HTML source** | Click "Source" tab when viewing an email |
| **API access** | Mailpit has a REST API at `http://localhost:8025/api/v1/` |

### Troubleshooting Mailpit

| Problem | Solution |
|---------|----------|
| **Mailpit won't start** | Check if port 1025 is already in use. Run `netstat -ano \| findstr :1025` on Windows |
| **Emails not appearing** | Make sure `EMAIL_PORT=1025` in `backend/.env` and restart Django |
| **Can't open web UI** | Make sure Mailpit is running. The web UI is at `http://localhost:8025` |
| **Email send errors in Django logs** | Check `backend/logs/app.log` for the error message |

### How the Code Sends Emails (Beginner Explanation)

When you trigger an email in EmpSphere, here's what happens behind the scenes:

1. **Frontend** calls an API endpoint (e.g., `POST /api/auth/send-otp/`)
2. **Controller** receives the request and validates it
3. **Service** (e.g., `OTPService`) generates the OTP and calls `EmailManager`
4. **EmailManager** calls `EmailService.send()`
5. **EmailService** uses Django's `EmailMultiAlternatives` to create the email
6. **Django** sends the email to the SMTP server configured in settings
7. **Mailpit** (running on port 1025) catches the email
8. **You** open `http://localhost:8025` to read the email

### Key Files for Email

| File | What it does |
|------|-------------|
| `backend/config/settings.py` | Reads email settings from `.env` (lines 168-179) |
| `backend/apps/common/email/email_service.py` | Sends the actual email using Django's SMTP backend |
| `backend/apps/common/email/email_templates.py` | Lists all email template names |
| `backend/apps/authentication/managers/email_manager.py` | Composes emails (subject, body, recipient) |
| `backend/templates/emails/otp_email.html` | HTML template for OTP emails |
| `backend/templates/emails/verify_email.html` | HTML template for email verification |
| `backend/templates/emails/forgot_password.html` | HTML template for password reset |
| `backend/.env` | Contains `EMAIL_PORT=1025` (Mailpit's port) |

---

## 9.2 Company Registration Code (3456)

### What is the Company Registration Code?

The **Company Registration Code** (also called `company_secret` in the code) is a secret password that a new admin must enter on the **Register** page to create an account. Only people who know this code can register as an admin.

### Current Code

The current company registration code is **`3456`**. This is set in `backend/.env`:

```env
COMPANY_REGISTRATION_SECRET=3456
```

### Where is the Company Code Used?

| File | What it does |
|------|-------------|
| `backend/.env` | Stores the actual secret value (`COMPANY_REGISTRATION_SECRET=3456`) |
| `backend/apps/common/config/settings.py` | Reads the secret from `.env` into the `settings` object (line 94) |
| `backend/apps/authentication/serializers/auth_serializer.py` | Validates the `company_secret` field against `settings.COMPANY_REGISTRATION_SECRET` (line 49) |
| `backend/apps/authentication/dtos/auth_dto.py` | `RegisterDTO` has a `company_secret` field (line 31) |
| `frontend/src/components/auth/RegisterForm.tsx` | Has a "Company Registration Secret" input field (line 108-117) |
| `frontend/src/types/auth.ts` | TypeScript type includes `company_secret: string` |

### How the Company Code Validation Works (Step by Step)

1. **User types the code** in the Register form under "Company Registration Secret"
2. **Frontend sends** the code in the registration request:
   ```json
   {
     "first_name": "John",
     "last_name": "Doe",
     "email": "john@example.com",
     "password": "Password@123",
     "confirm_password": "Password@123",
     "company_secret": "3456"
   }
   ```
3. **Backend receives** the request at `POST /api/auth/register/`
4. **RegisterSerializer validates** the request. In `validate()`, it checks:
   ```python
   if attrs.get("company_secret") != settings.COMPANY_REGISTRATION_SECRET:
       raise serializers.ValidationError(
           {"company_secret": "Invalid company registration secret."}
       )
   ```
5. **If the code is wrong** → the backend returns a 400 error: `"Invalid company registration secret."`
6. **If the code is correct** → the serializer continues and creates the admin account
7. **`company_secret` is removed** from the data before it reaches the service layer (security — we never store the secret)

### How to Change the Company Code

If you want to change the code from `3456` to something else:

1. Open `backend/.env`
2. Change the value:
   ```env
   COMPANY_REGISTRATION_SECRET=my-new-code
   ```
3. **Restart the Django server** for the change to take effect:
   ```bash
   cd backend
   python manage.py runserver 8000
   ```
4. Now new admins must enter `my-new-code` to register

### Important Security Notes

- **Never share this code publicly** — it's the key to creating admin accounts
- **Never hardcode it** in the frontend — it's only stored on the backend in `.env` (which is in `.gitignore`)
- **In production**, use a longer, more random code (like a UUID or random string)

### Testing the Company Code with Postman

When testing the registration endpoint in Postman, include `company_secret` in the request body:

```json
POST /api/auth/register/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "Password@123",
  "confirm_password": "Password@123",
  "company_secret": "3456"
}
```

If you get `"Invalid company registration secret."`, double-check that `backend/.env` has `COMPANY_REGISTRATION_SECRET=3456` and that the Django server was restarted after any changes.

---

## 10. Google Authentication

### Frontend
**File**: `frontend/src/components/auth/LoginForm.tsx`

- Loads **Google Identity Services (GIS)** from `https://accounts.google.com/gsi/client`
- Uses `google.accounts.id.initialize()` with the `GOOGLE_CLIENT_ID`
- Renders the official Google sign-in button
- On credential response, sends the `id_token` to the backend

### Backend
**File**: `backend/apps/common/security/google_manager.py`

- `GoogleManager.verify_id_token()` — verifies the Google ID token using `google.oauth2.id_token`
- `GoogleManager.extract_user_info()` — extracts user fields from Google claims

### Google Login Service
**File**: `backend/apps/authentication/services/auth_service.py` → `GoogleLoginService`

1. Verify the Google ID token
2. Extract user info (google_id, email, name, profile image)
3. Look up user by `google_id` → if not found, look up by `email`
4. If no user exists → create a new user with:
   - `login_provider = "GOOGLE"`
   - `google_id` set
   - `is_email_verified = True`
   - `role = "EMPLOYEE"`
5. If user exists → update `google_id` and `is_email_verified`
6. Generate access + refresh tokens
7. Return tokens to frontend

### Frontend After Google Login
1. `googleLogin` thunk stores tokens in `localStorage`
2. Redux state is updated with the user
3. User is redirected to their role-based dashboard

---

## 11. RBAC & Role Hierarchy

### Role Definitions
**File**: `backend/apps/common/core/roles.py`

```python
class Role(IntEnum):
    EMPLOYEE = 1
    HR_MANAGER = 2
    ADMIN = 3
    SUPER_ADMIN = 4
```

### Role Hierarchy (lowest → highest)
```
EMPLOYEE < HR_MANAGER < ADMIN < SUPER_ADMIN
```

### Role Permission Helper
**File**: `backend/apps/common/permissions/role_permission.py`

- `has_privilege(user_role, required_role)` — checks if user_role >= required_role
- `can_manage_user(actor_role, target_role)` — who can manage whom:
  - SUPER_ADMIN → can manage everyone
  - ADMIN → can manage HR_MANAGER and EMPLOYEE
  - HR_MANAGER → can manage EMPLOYEE
  - EMPLOYEE → can manage nobody
- `can_assign_role(actor_role, target_role)` — used by create-user endpoint
- `owns_resource(actor, resource_user_id)` — checks if user owns a resource

### Role Decorator
**File**: `backend/apps/common/decorators/permission.py`

- `@require_role(Role.ADMIN, Role.SUPER_ADMIN)` — restricts a view to specific roles

### DRF Permission Classes
**File**: `backend/apps/authentication/permissions.py`

- `IsAuthenticatedUser` — default permission for all authenticated endpoints
- `IsSuperAdmin` — only SUPER_ADMIN

---

## 12. Middleware & Exception Handling

### Middleware (in `settings.py`)
```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    # ... Django defaults ...
    "apps.common.middleware.request_logger.RequestLoggerMiddleware",
    "apps.common.middleware.exception_middleware.ExceptionMiddleware",
]
```

### JWT Authentication Middleware
**File**: `backend/apps/common/middleware/authentication.py`

- Custom DRF authentication class
- Validates Bearer access tokens
- Loads user from MongoDB

### Exception Middleware
**File**: `backend/apps/common/middleware/exception_middleware.py`

- Catches unhandled exceptions
- Returns a standardized JSON error response

### Custom Exceptions
**File**: `backend/apps/common/exceptions/custom_exception.py`

| Exception | HTTP Status | Purpose |
|-----------|-------------|---------|
| `ValidationException` | 400 | Request validation failed |
| `UnauthorizedException` | 401 | Authentication failed |
| `ForbiddenException` | 403 | Permission denied |
| `NotFoundException` | 404 | Resource not found |
| `ConflictException` | 409 | Duplicate resource |
| `InternalServerException` | 500 | Unexpected server error |

### Global Exception Handler
**File**: `backend/apps/common/exceptions/exception_handler.py`

- Registered as the DRF `EXCEPTION_HANDLER`
- Converts all exceptions into the standard `{success, message, errors}` format

---

## 13. ApiResponse

**File**: `backend/apps/common/responses/api_response.py`

### Success Response
```json
{
    "success": true,
    "message": "Login successful.",
    "data": { ... },
    "meta": null
}
```

### Error Response
```json
{
    "success": false,
    "message": "Invalid email or password.",
    "errors": null
}
```

### Paginated Response
```json
{
    "success": true,
    "message": "Data fetched successfully.",
    "data": [ ... ],
    "meta": {
        "page": 1,
        "page_size": 10,
        "total_records": 100,
        "total_pages": 10
    }
}
```

---

## 14. MongoDB / PyMongo

### Connection Manager
**File**: `backend/apps/common/database/mongo.py`

- Singleton pattern — one MongoDB connection reused across the app
- Uses `MongoClient` with connection pooling (max 50, min 5)
- Exposes `get_collection(name)` to access collections

### Configuration
**File**: `backend/apps/common/config/settings.py`

- `MONGO_URI` — default `mongodb://localhost:27017`
- `DATABASE_NAME` — default `empsphere_db`

### Collections
**File**: `backend/apps/common/core/collections.py`

| Collection | Purpose |
|------------|---------|
| `users` | User accounts |
| `tokens` | Blacklisted refresh tokens |
| `otps` | One-time passwords |
| `sequences` | Atomic sequence counters |
| `departments` | Department records |
| `designations` | Designation records |
| `organizations` | Organization records |
| `audit_logs` | Audit log entries |
| `activity_logs` | Activity logs |

### Document Helper
**File**: `backend/apps/common/utils/document_helper.py`

- Adds `created_at`, `updated_at`, `created_by`, `updated_by`, `is_deleted`, `deleted_at`, `deleted_by` metadata

---

## 15. Frontend Routing

**File**: `frontend/src/routes/AppRoutes.tsx`

### Public Routes
| Route | Component |
|-------|-----------|
| `/login` | LoginPage |
| `/register` | RegisterPage |
| `/forgot-password` | ForgotPasswordPage |
| `/reset-password` | ResetPasswordPage |
| `/verify-email` | VerifyEmailPage |

### Protected Routes (inside `ProtectedRoute`)
| Route | Component | Required Role |
|-------|-----------|---------------|
| `/dashboard` | DashboardRedirect | Any authenticated |
| `/dashboard/super-admin` | SuperAdminDashboardPage | SUPER_ADMIN |
| `/dashboard/admin` | AdminDashboardPage | ADMIN |
| `/dashboard/hr` | HRDashboardPage | HR_MANAGER |
| `/dashboard/employee` | EmployeeDashboardPage | EMPLOYEE |
| `/change-password` | ChangePasswordPage | Any authenticated |
| `/profile` | ProfilePage | Any authenticated |
| `/departments` | DepartmentsPage | Any authenticated |
| `/users/create` | CreateUserPage | Any authenticated |

### Other Routes
| Route | Component |
|-------|-----------|
| `/unauthorized` | UnauthorizedPage |
| `/` | Redirect to `/dashboard` |
| `*` | NotFoundPage |

---

## 16. Redux Toolkit State Management

**File**: `frontend/src/store/index.ts`

### Store Configuration
```typescript
reducer: {
    auth: authReducer,
    user: userReducer,
    department: departmentReducer,
}
```

### Auth Slice
**File**: `frontend/src/store/slices/authSlice.ts`

State:
```typescript
{
    user: User | null,
    loading: boolean,
    initializing: boolean,
    error: string | null
}
```

Actions (async thunks):
- `login` — calls `/auth/login/`, stores tokens
- `register` — calls `/auth/register/`
- `fetchMe` — calls `/auth/me/` to get user profile
- `logoutUser` — calls `/auth/logout/`, clears tokens
- `googleLogin` — calls `/auth/google-login/`, stores tokens

Reducers:
- `clearAuth` — clears user state
- `setUser` — sets user directly
- `setInitialized` — marks initialization complete

### User Slice
**File**: `frontend/src/store/slices/userSlice.ts`

- Minimal — caches user profiles by ID

### Department Slice
**File**: `frontend/src/store/slices/departmentSlice.ts`

- Manages department list state
- Actions: `fetchDepartments`, `createDepartment`, `updateDepartment`, `deleteDepartment`

### Auth Middleware
**File**: `frontend/src/store/middleware/authMiddleware.ts`

- Clears tokens on logout

---

## 17. Axios Configuration & Interceptors

**File**: `frontend/src/config/axios.ts`

### Request Interceptor
- Attaches `Authorization: Bearer <access_token>` to every request

### Response Interceptor
- On **401** (unauthorized):
  1. Skip if the request was already retried
  2. Skip for login/refresh endpoints
  3. Get the refresh token from `localStorage`
  4. Call `/auth/refresh-token/`
  5. Store the **new access token AND new refresh token** (rotation)
  6. Retry the original request
  7. If refresh fails → clear tokens, dispatch `auth:expired` event

### Auth Expired Event
- `AUTH_EXPIRED_EVENT = "auth:expired"`
- `AppBootstrap` listens for this event
- On event: clears tokens, clears Redux state, redirects to `/login`

---

## 18. Authentication Flow (Step by Step)

### Login Flow
```
Frontend (LoginForm)
    ↓ POST /api/auth/login/ {email, password}
Backend (LoginController)
    ↓ LoginSerializer validates
    ↓ LoginDTO
Backend (LoginService)
    ↓ UserRepository.get_by_email()
    ↓ PasswordManager.verify_password()
    ↓ AuthenticationValidator.validate_login()
    ↓ JWTManager.generate_access_token()
    ↓ JWTManager.generate_refresh_token()
    ↓ UserRepository.update(last_login)
    ↓ AuditService.log()
    ↓ Returns {user_id, email, role, access_token, refresh_token}
Frontend (authSlice login thunk)
    ↓ TokenUtil.setTokens(access, refresh)
    ↓ Redux state updated
    ↓ navigate(getDashboardRoute(role))
```

### Registration Flow
```
Frontend (RegisterForm)
    ↓ POST /api/auth/register/ {first_name, last_name, email, phone, password, confirm_password, company_secret}
Backend (RegisterController)
    ↓ RegisterSerializer validates (checks company_secret == "3456", forces role=ADMIN)
    ↓ RegisterDTO
Backend (RegisterService)
    ↓ UserRepository.email_exists() → ConflictException if exists
    ↓ EmployeeCodeManager.generate() → EMP000001
    ↓ PasswordManager.hash_password()
    ↓ UserSchema.create_document()
    ↓ UserRepository.create()
    ↓ Returns {user_id}
Frontend (authSlice register thunk)
    ↓ navigate("/login")
```

**Important:** The registration flow requires the **Company Registration Code (`3456`)**. The `RegisterSerializer` validates this code against `settings.COMPANY_REGISTRATION_SECRET` before allowing the account to be created. If the code is wrong, the backend returns `"Invalid company registration secret."` and no account is created.

### Logout Flow
```
Frontend (Navbar → Logout button)
    ↓ POST /api/auth/logout/ {refresh_token}
Backend (LogoutController)
    ↓ LogoutService.logout()
    ↓ TokenBlacklistManager.blacklist(refresh_token)
Frontend (authSlice logoutUser thunk)
    ↓ TokenUtil.clear()
    ↓ Redux state cleared
    ↓ navigate("/login")
```

---

## 19. Protected Routes

**File**: `frontend/src/routes/ProtectedRoute.tsx`

- Uses `useAuth()` hook
- If `initializing` → show loading spinner
- If not authenticated → redirect to `/login`
- If authenticated → render child routes via `<Outlet />`

**File**: `frontend/src/routes/RequireRole.tsx`

- Checks if the user's role is in the allowed roles list
- If not → redirect to the user's own dashboard
- If yes → render children

---

## 20. Role-Based Dashboard Routing

**File**: `frontend/src/routes/DashboardRedirect.tsx`

- Redirects from `/dashboard` to the role-specific dashboard

**File**: `frontend/src/utils/constants.ts`

```typescript
ROLE_DASHBOARD_ROUTES = {
    SUPER_ADMIN: "/dashboard/super-admin",
    ADMIN: "/dashboard/admin",
    HR_MANAGER: "/dashboard/hr",
    EMPLOYEE: "/dashboard/employee",
}
```

### Sidebar Navigation
- **SUPER_ADMIN**: Dashboard, Create User, Departments, Employees, Attendance, Leave, Payroll, Reports
- **ADMIN**: Dashboard, Create User, Departments, Employees, Attendance, Leave, Payroll, Reports
- **HR_MANAGER**: Dashboard, Create User, Departments, Employees, Attendance, Leave
- **EMPLOYEE**: Dashboard, Attendance, Leave, Payroll

> Note: Employees, Attendance, Leave, Payroll, Reports are **placeholder links** (marked "Soon") — they are Week 2+ features.

---

## 21. Profile Functionality

### View Profile
**File**: `frontend/src/pages/profile/ProfilePage.tsx`

- Displays user's avatar, name, email, role, employee code
- Uses `useAuth()` to get the current user

### Update Profile
- `PATCH /api/auth/profile/` — updates first_name, last_name, phone
- Backend: `UpdateProfileService` → `UserRepository.update()`
- Frontend: `userService.updateProfile()` → `refreshProfile()` → `setUser()`

### Upload Profile Image
- `POST /api/auth/profile/upload-image/` — uploads a file
- Backend: `UploadProfileImageService` → `FileManager.save()` → `UserRepository.update()`
- Frontend: `userService.uploadProfileImage()` → `refreshProfile()` → `setUser()`

### Backend Profile Endpoints
**File**: `backend/apps/authentication/controllers/auth_controller.py`

- `MeController` — `GET /api/auth/me/` returns sanitized profile
- `ProfileController` — `PATCH /api/auth/profile/` and `POST /api/auth/profile/upload-image/`

---

## 22. Change Password

### Frontend
**File**: `frontend/src/components/auth/ChangePasswordForm.tsx`

- User enters current password, new password, confirm password
- Validates new password matches confirmation
- Calls `userService.changePassword()`

### API
`POST /api/auth/change-password/`

### Backend Flow
```
ChangePasswordController
    ↓ ChangePasswordSerializer validates
    ↓ ChangePasswordDTO
ChangePasswordService
    ↓ UserRepository.get_by_id()
    ↓ PasswordManager.verify_password(old_password) → UnauthorizedException if wrong
    ↓ PasswordManager.hash_password(new_password)
    ↓ UserRepository.update({password: hashed})
```

### Token Behavior
- **No token invalidation** — the user stays logged in after changing password
- The access token and refresh token remain valid

---

## 23. Forgot Password

### Frontend
**File**: `frontend/src/components/auth/ForgotPasswordForm.tsx`

- User enters email
- Calls `authService.forgotPassword()`
- Shows "If an account exists, a reset link has been sent" (doesn't reveal if email exists)

### API
`POST /api/auth/forgot-password/`

### Backend Flow
```
ForgotPasswordController
    ↓ ForgotPasswordSerializer validates
    ↓ ForgotPasswordDTO
ForgotPasswordService
    ↓ UserRepository.get_by_email()
    ↓ If user not found → silently return (don't reveal)
    ↓ Create JWT with token_type="password_reset", exp=30min
    ↓ EmailManager.send_forgot_password_email()
```

### Email
- Sends a link: `{FRONTEND_URL}/reset-password?token={token}`

---

## 24. Reset Password

### Frontend
**File**: `frontend/src/components/auth/ResetPasswordForm.tsx`

- Reads `token` from URL query params
- User enters new password + confirm
- Calls `authService.resetPassword()`

### API
`POST /api/auth/reset-password/`

### Backend Flow
```
ResetPasswordController
    ↓ ResetPasswordSerializer validates
    ↓ ResetPasswordDTO
ResetPasswordService
    ↓ jwt.decode(token) → UnauthorizedException if invalid
    ↓ Check token_type == "password_reset"
    ↓ Get user_id from payload
    ↓ PasswordManager.hash_password(new_password)
    ↓ UserRepository.update({password: hashed})
```

---

## 25. Email Verification

### Two Methods

#### Method 1: JWT Token (via email link)
- `EmailManager.send_verification_email()` sends a link: `{FRONTEND_URL}/verify-email?token={token}`
- `VerifyEmailService.verify_email()` decodes the JWT and sets `is_email_verified = True`
- **Note**: This method exists in the backend but the frontend `VerifyEmailPage` uses OTP instead

#### Method 2: OTP (via frontend form)
**File**: `frontend/src/components/auth/VerifyEmailForm.tsx`

1. User enters email → clicks "Send OTP"
2. `POST /api/auth/send-otp/` with `{email, purpose: "email_verification"}`
3. Backend generates OTP, stores it hashed, emails it
4. User enters the 6-digit OTP
5. `POST /api/auth/verify-otp/` with `{email, otp, purpose: "email_verification"}`
6. Backend verifies OTP, marks it used, sets `is_email_verified = True`
7. Frontend redirects to `/login`

---

## 26. Google Login Flow

### Frontend
1. `LoginForm` loads Google Identity Services script
2. Renders the Google sign-in button
3. User clicks the button → Google account chooser opens
4. User selects an account → Google returns a `credential` (ID token)
5. `googleLogin(credential)` thunk is dispatched

### API
`POST /api/auth/google-login/` with `{id_token: credential}`

### Backend
1. `GoogleLoginController` validates the request
2. `GoogleLoginService.google_login()`:
   - `GoogleManager.verify_id_token()` — verifies the Google token
   - `GoogleManager.extract_user_info()` — extracts user data
   - Look up user by `google_id` → if not found, by `email`
   - If no user → create new user (role=EMPLOYEE, login_provider=GOOGLE, is_email_verified=True)
   - If user exists → update `google_id` and `is_email_verified`
   - Generate access + refresh tokens
3. Returns `{user_id, email, role, access_token, refresh_token}`

### Frontend
1. `googleLogin` thunk stores tokens in `localStorage`
2. Redux state updated with user
3. `navigate(getDashboardRoute(role))` — redirects to role dashboard

---

## 27. Important File Explanations

### Backend Files

| File | What it does | What calls it | What it calls |
|------|-------------|---------------|---------------|
| `config/settings.py` | Django settings, DRF config, JWT config, logging | Django startup | — |
| `config/urls.py` | Root URL routing | Django | `apps.authentication.urls`, `apps.organization.urls` |
| `apps/authentication/urls.py` | Auth API routes | `config/urls.py` | All auth controllers |
| `apps/authentication/controllers/auth_controller.py` | Auth API endpoints | `urls.py` | Auth services |
| `apps/authentication/controllers/otp_controller.py` | OTP API endpoints | `urls.py` | OTP services |
| `apps/authentication/controllers/password_controller.py` | Password API endpoints | `urls.py` | Password services |
| `apps/authentication/controllers/user_controller.py` | Create user endpoint | `urls.py` | CreateUserService |
| `apps/authentication/services/auth_service.py` | Auth business logic | Controllers | Repositories, Managers |
| `apps/authentication/services/otp_service.py` | OTP business logic | OTP controllers | OTPManager, Repositories |
| `apps/authentication/services/password_service.py` | Password business logic | Password controllers | Repositories, Managers |
| `apps/authentication/services/user_service.py` | User creation logic | User controller | Repositories, Managers |
| `apps/authentication/repositories/user_repository.py` | User DB operations | Services | BaseRepository |
| `apps/authentication/repositories/otp_repository.py` | OTP DB operations | OTP services | BaseRepository |
| `apps/authentication/repositories/sequence_repository.py` | Sequence generation | EmployeeCodeManager | MongoDB |
| `apps/authentication/managers/otp_manager.py` | OTP generation/hashing | OTP services | OTPRepository, EmailManager |
| `apps/authentication/managers/email_manager.py` | Email composition | OTPManager, PasswordService | EmailService |
| `apps/authentication/managers/jwt_manager.py` | JWT wrapper | Auth services | CommonJWTManager |
| `apps/authentication/managers/password_manager.py` | Password wrapper | Auth services | CommonPasswordManager |
| `apps/authentication/managers/token_blacklist_manager.py` | Token blacklisting | LogoutService, RefreshTokenService | MongoDB |
| `apps/authentication/managers/employee_code_manager.py` | Employee code generation | RegisterService, CreateUserService | SequenceRepository |
| `apps/authentication/schemas/user_schema.py` | User document structure | RegisterService, CreateUserService, GoogleLoginService | — |
| `apps/authentication/serializers/auth_serializer.py` | Auth request validation | Auth controllers | Validators |
| `apps/authentication/serializers/otp_serializer.py` | OTP request validation | OTP controllers | Validators |
| `apps/authentication/serializers/password_serializer.py` | Password request validation | Password controllers | Validators |
| `apps/authentication/serializers/user_serializer.py` | User request validation | User controller | Validators |
| `apps/authentication/validators/auth_validator.py` | Auth business rules | LoginService | UserRepository |
| `apps/authentication/validators/email_validator.py` | Email validation | Serializers | Regex |
| `apps/authentication/validators/password_validator.py` | Password validation | Serializers | Regex |
| `apps/authentication/validators/user_validator.py` | Role validation | CreateUserService | RolePermission |
| `apps/authentication/permissions.py` | DRF permission classes | DRF settings | RolePermission |
| `apps/common/base/base_controller.py` | Base API response methods | All controllers | ApiResponse |
| `apps/common/base/base_service.py` | Base audit logging | Services | AuditService |
| `apps/common/base/base_repository.py` | Base CRUD operations | All repositories | MongoDB |
| `apps/common/database/mongo.py` | MongoDB connection | All repositories | PyMongo |
| `apps/common/config/settings.py` | App settings | All modules | Environment |
| `apps/common/core/roles.py` | Role definitions | Permissions, decorators | — |
| `apps/common/core/collections.py` | Collection names | Repositories | — |
| `apps/common/core/messages.py` | Message constants | Exceptions | — |
| `apps/common/core/regex.py` | Validation regex | Validators | — |
| `apps/common/core/status.py` | HTTP status codes | Exceptions, ApiResponse | — |
| `apps/common/security/jwt_manager.py` | JWT creation/decode | Auth services | PyJWT |
| `apps/common/security/password_manager.py` | Password hashing | Auth services | Passlib |
| `apps/common/security/google_manager.py` | Google token verification | GoogleLoginService | Google Auth |
| `apps/common/email/email_service.py` | Email sending | EmailManager | Django Email |
| `apps/common/email/email_templates.py` | Template names | EmailManager | — |
| `apps/common/exceptions/custom_exception.py` | Custom exceptions | All services | — |
| `apps/common/exceptions/exception_handler.py` | Global exception handler | DRF settings | — |
| `apps/common/middleware/authentication.py` | JWT authentication | DRF settings | UserRepository |
| `apps/common/middleware/exception_middleware.py` | Exception middleware | Django settings | — |
| `apps/common/middleware/request_logger.py` | Request logging | Django settings | — |
| `apps/common/permissions/role_permission.py` | Role permission helpers | Services, decorators | Roles |
| `apps/common/decorators/permission.py` | Role decorator | Department controller | RolePermission |
| `apps/common/responses/api_response.py` | Standard API responses | BaseController | — |
| `apps/common/storage/file_manager.py` | File uploads | UploadProfileImageService | Django Storage |
| `apps/common/utils/document_helper.py` | Document metadata | BaseRepository | — |
| `apps/activity_logs/services/audit_service.py` | Audit logging | BaseService | MongoDB |

### Frontend Files

| File | What it does | What calls it | What it calls |
|------|-------------|---------------|---------------|
| `src/main.tsx` | React entry point | `index.html` | `App.tsx` |
| `src/App.tsx` | Root component | `main.tsx` | Redux Provider, Router, AppBootstrap, AppRoutes |
| `src/components/AppBootstrap.tsx` | Session restore | `App.tsx` | fetchMe, auth:expired listener |
| `src/config/axios.ts` | Axios instance | All services | TokenUtil, authService |
| `src/config/env.ts` | Environment access | All modules | — |
| `src/services/api.ts` | Typed HTTP wrapper | All services | axios |
| `src/services/auth.service.ts` | Auth API calls | authSlice, forms | api |
| `src/services/user.service.ts` | User API calls | ProfilePage, ChangePasswordForm | api |
| `src/services/department.service.ts` | Department API calls | departmentSlice | api |
| `src/store/index.ts` | Redux store | `App.tsx` | Slices, middleware |
| `src/store/slices/authSlice.ts` | Auth state | useAuth hook | authService, userService, TokenUtil |
| `src/store/slices/userSlice.ts` | User cache | — | — |
| `src/store/slices/departmentSlice.ts` | Department state | DepartmentsPage | departmentService |
| `src/store/middleware/authMiddleware.ts` | Token cleanup | store | TokenUtil |
| `src/hooks/useAuth.ts` | Auth hook | Components | authSlice |
| `src/routes/AppRoutes.tsx` | Route config | `App.tsx` | All pages |
| `src/routes/ProtectedRoute.tsx` | Auth guard | AppRoutes | useAuth |
| `src/routes/RequireRole.tsx` | Role guard | AppRoutes | useAuth |
| `src/routes/DashboardRedirect.tsx` | Role dashboard redirect | AppRoutes | useAuth |
| `src/utils/constants.ts` | Roles, routes, nav | All modules | — |
| `src/utils/token.ts` | Token storage | authSlice, axios | localStorage |
| `src/utils/helpers.ts` | Utility functions | Components | — |
| `src/types/auth.ts` | Auth types | All modules | — |
| `src/types/api.ts` | API types | services | — |
| `src/types/user.ts` | User types | services | — |
| `src/types/department.ts` | Department types | services | — |
| `src/components/auth/LoginForm.tsx` | Login form | LoginPage | useAuth, Google |
| `src/components/auth/RegisterForm.tsx` | Register form | RegisterPage | useAuth |
| `src/components/auth/VerifyEmailForm.tsx` | OTP verification | VerifyEmailPage | authService |
| `src/components/auth/ForgotPasswordForm.tsx` | Forgot password | ForgotPasswordPage | authService |
| `src/components/auth/ResetPasswordForm.tsx` | Reset password | ResetPasswordPage | authService |
| `src/components/auth/ChangePasswordForm.tsx` | Change password | ChangePasswordPage | userService |
| `src/components/users/CreateUserForm.tsx` | Create user | CreateUserPage | userService |
| `src/components/layout/DashboardLayout.tsx` | Layout wrapper | AppRoutes | Sidebar, Navbar, Outlet |
| `src/components/layout/Sidebar.tsx` | Navigation sidebar | DashboardLayout | useAuth, constants |
| `src/components/layout/Navbar.tsx` | Top navbar | DashboardLayout | useAuth, Avatar |
| `src/pages/profile/ProfilePage.tsx` | Profile page | AppRoutes | userService, useAuth |
| `src/pages/dashboard/*.tsx` | Role dashboards | AppRoutes | DashboardContent |

---

## 28. Missing Features

The following features are **MISSING** (not implemented in Week 1):

1. **Employee Management** — No employee CRUD endpoints or pages
2. **Attendance** — No attendance tracking
3. **Leave Management** — No leave request/approval system
4. **Payroll** — No payroll generation or payslips
5. **Reports** — No report generation
6. **Notifications** — No notification system
7. **Designation Management** — No designation CRUD (only referenced in user schema)
8. **Organization Management** — No organization CRUD (only referenced in department schema)
9. **Welcome Email** — `EmailTemplates.WELCOME` exists but is never used
10. **Email Verification Link Flow** — The backend has `VerifyEmailService` (JWT-based) but the frontend uses OTP instead; the JWT-based email verification link flow is not wired up in the frontend
11. **First Super Admin Setup** — No mechanism to create the first SUPER_ADMIN (mentioned as "will be added later" in `AuthenticationValidator`)
12. **Phone Validation** — `AuthenticationValidator.validate_registration()` has a comment "Phone validation will be added later"
13. **Role Permission Validation in Registration** — `AuthenticationValidator.validate_registration()` has a comment "Role permission validation will be added later"
14. **Razorpay Integration** — `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are in settings but no payment code exists
15. **React Query** — `@tanstack/react-query` is in `package.json` but not used
16. **React Hook Form** — `react-hook-form` and `zod` are in `package.json` but not used
17. **jwt-decode** — `jwt-decode` is in `package.json` but not used

---

## 29. Partially Implemented Features

1. **Department Management** — CRUD exists in backend (`DepartmentController`, `DepartmentService`, `DepartmentRepository`) and frontend (`DepartmentsPage`, `departmentSlice`), but it's minimal and not fully integrated with user management
2. **Email Verification** — Two methods exist (JWT link + OTP), but only OTP is wired to the frontend
3. **Profile Image Upload** — Backend supports it, frontend has the UI, but the image URL is stored as a local path (not a full URL)
4. **Audit Logging** — `BaseService.log_activity()` exists and is used by LoginService and CreateUserService, but not by all services
5. **Request Logger Middleware** — Exists in `apps/common/middleware/request_logger.py` but its implementation wasn't fully verified
6. **Role-Based Navigation** — Sidebar shows placeholder links for future modules (marked "Soon")
7. **User Management** — Only `create-user` is implemented; no list, update, delete, or detail endpoints

---

## 30. Potential Bugs

1. **`AuthenticationValidator.validate_registration()`** — Uses `CustomException` with default status 400 instead of `ConflictException` (409) for duplicate email. However, `RegisterService` already checks `email_exists()` and raises `ConflictException`, so this validator is redundant.

2. **`VerifyEmailService.verify_email()`** — Uses `settings.JWT_SECRET` directly instead of the `JWTManager.decode_token()` method. If `JWT_SECRET` is empty, this could fail.

3. **`ForgotPasswordService`** — Creates a JWT with `token_type="password_reset"` but doesn't include a `jti` claim. This means the reset token cannot be blacklisted/revoked.

4. **`ResetPasswordService`** — Doesn't check if the user exists before updating. If the user was deleted, the update would silently fail.

5. **`ChangePasswordService`** — Doesn't invalidate existing tokens after a password change. The user stays logged in on all devices.

6. **`GoogleLoginService`** — When creating a new Google user, `employee_code` is set to `None`. This could cause issues if other parts of the app expect a valid employee code.

7. **`OTPManager.create_and_send()`** — Returns the plaintext OTP. The docstring says "for logging/dev" but this could be a security risk if accidentally logged.

8. **`TokenBlacklistManager.blacklist()`** — Uses `datetime.utcfromtimestamp(exp)` which is deprecated in Python 3.12+.

9. **`BaseRepository.get_by_id()`** — Uses `ObjectId(document_id)`. If an invalid ObjectId string is passed, it raises `bson.errors.InvalidId` which is not caught.

10. **`JWTAuthentication.authenticate()`** — Loads the user from MongoDB on every request. This is a performance concern for high-traffic apps.

11. **`frontend/src/types/auth.ts`** — `ResetPasswordPayload` includes `email` and `otp` fields, but the actual `ResetPasswordForm` only sends `token` and `new_password`. The type is misleading.

12. **`frontend/src/components/auth/LoginForm.tsx`** — The Google button is rendered inside a `<form>`. If the Google button is clicked, it might trigger form submission.

13. **`frontend/src/components/auth/VerifyEmailForm.tsx`** — After successful OTP verification, it navigates to `/login` but doesn't show a success message.

14. **`frontend/src/components/auth/ChangePasswordForm.tsx`** — After successful password change, it navigates to `/dashboard` after 1.5 seconds. If the user's token expires during this time, they'd be redirected to login.

15. **`frontend/src/store/slices/authSlice.ts`** — The `login` thunk stores tokens but doesn't call `fetchMe` afterward. The user object only has `_id`, `email`, and `role` — missing `full_name`, `profile_image`, etc. until a page calls `fetchMe`.

16. **`frontend/src/config/axios.ts`** — The refresh interceptor doesn't handle concurrent requests. If multiple requests fail with 401 simultaneously, multiple refresh calls could be made.

17. **`backend/apps/authentication/urls.py`** — The `profile/upload-image/` route uses the same `ProfileController` as `profile/`. The `post` method handles both profile updates and image uploads, which could be confusing.

18. **`backend/apps/common/middleware/authentication.py`** — The `authenticate()` method returns `(user, token)` but the token is never used. This is fine but slightly wasteful.

19. **`backend/apps/authentication/serializers/auth_serializer.py`** — `RegisterSerializer` has a `role` field that is always overridden to `"EMPLOYEE"` in `validate()`. This is intentional (security) but could confuse API consumers.

20. **`frontend/src/components/users/CreateUserForm.tsx`** — The `CREATEABLE_ROLES` map is duplicated on the frontend. The backend also enforces this via `RolePermission.can_assign_role()`. This is defense-in-depth but could drift if roles change.

---

## Summary

EmpSphere Week 1 delivers a **complete authentication system** with:

- ✅ JWT-based authentication (access + refresh tokens)
- ✅ Refresh token rotation with blacklisting
- ✅ OTP-based email verification
- ✅ Password management (change, forgot, reset)
- ✅ Google OAuth2 login
- ✅ Role-based access control (4 roles)
- ✅ Profile management (view, update, image upload)
- ✅ User creation with role hierarchy enforcement
- ✅ Department management (basic CRUD)
- ✅ Standardized API responses
- ✅ Global exception handling
- ✅ Audit logging
- ✅ MongoDB integration

The architecture follows a clean **Controller → Service → Repository** pattern with shared base classes, making it easy to extend for Week 2+ features (Employee Management, Attendance, Payroll, etc.).