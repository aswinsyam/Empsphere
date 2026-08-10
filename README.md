# EmpSphere — Employee Management & Payroll Platform

EmpSphere is a full-stack employee management and payroll platform. This repository contains the **Week 1** deliverables: project foundation, a complete authentication system with JWT + RBAC, and role-based dashboards.

- **Backend**: Django + Django REST Framework + MongoDB (PyMongo)
- **Frontend**: React + TypeScript + Tailwind CSS + Redux Toolkit
- **API Testing**: Postman collection included

---

## 1. What's Included (Week 1)

### Backend (`backend/`)

- **Project setup** — Django + DRF + MongoDB (PyMongo), centralized settings, CORS, logging.
- **Authentication module** (`apps/authentication`) — Register, Login, Logout, Refresh Token, Change Password, Forgot Password, Reset Password, Email Verification, `/me`, and Google Login (optional).
- **JWT Authentication** — Access + refresh tokens with automatic rotation and token blacklisting on logout.
- **RBAC (Role-Based Access Control)** — Four roles: `SUPER_ADMIN`, `ADMIN`, `HR_MANAGER`, `EMPLOYEE`, with role-permission mappings enforced on protected APIs.
- **Seed data** — `seed_rbac` command seeds all roles, permissions, and one default Super Admin.
- **Audit logs** (`apps/activity_logs`) — Records key actions for an audit trail.
- **Global exception handler** — All errors normalized into a consistent response shape.
- **Standard API responses** — Every endpoint returns the `{ success, message, data }` envelope.
- **Logging** — Request logging middleware + file/console loggers.
- **Security managers** — Password hashing, JWT tokens, Google OAuth verification, token blacklist.

### Frontend (`frontend/`)

- **React + TypeScript + Tailwind CSS** — Vite-powered SPA.
- **Redux Toolkit** — Auth state (access token, refresh token, logged-in user) + async actions.
- **Axios** — Configured instance with JWT attach, automatic token refresh on 401, and auto-logout when refresh fails.
- **Auth pages** — Login, Register, Forgot Password, Reset Password, Change Password, Verify Email.
- **Protected routes** — Unauthenticated users are redirected to login.
- **Role-based redirect** — After login each user is sent to their role-specific dashboard.
- **Four dashboards** — Super Admin, Admin, HR Manager, Employee.
- **Sidebar** — Role-aware navigation with placeholder links for future modules (Week 2+).
- **Navbar** — Shows the user profile avatar with a dropdown (Change Password, Logout).
- **User profile** — Profile card with avatar, name, role, email, employee code, and email-verification status.
- **Dashboard cards (placeholder)** — Statistics cards with placeholder values.
- **Recent activity (placeholder)** — A placeholder activity list.

### Postman

- `postman/EmpSphere_Week1.postman_collection.json` — Ready-to-import collection covering all auth endpoints.

---

## 2. Not in Week 1 (Moved to Week 2+)

These business modules are **out of scope for Week 1** and will be built in later weeks:

- ❌ Department CRUD
- ❌ Designation CRUD
- ❌ Employee CRUD
- ❌ Attendance
- ❌ Leave Management
- ❌ Payroll
- ❌ Reports
- ❌ Notifications

> Note: The `organization` app (departments) currently exists in the backend as a working reference implementation of the layered pattern. It is not part of the Week 1 scope and will be fully integrated in **Week 2 – Organization**.

---

## 3. Week Breakdown

| Week | Focus | Deliverables |
|------|-------|--------------|
| **Week 1** | Foundation & Authentication | Backend setup, auth APIs, JWT, RBAC, seed roles + Super Admin, React setup, auth UI, Redux Toolkit, protected routes, role-based dashboards |
| **Week 2** | Organization | Department CRUD, Designation CRUD, Employee CRUD, Profile Management |
| **Week 3** | HR Operations | Attendance, Leave Management, Notifications, Activity Logs, Search/Filter/Pagination |
| **Week 4** | Payroll & Reports | Payroll, Payslips, Reports, Dashboard Analytics, File Uploads, Final Testing, Deployment |

---

## 4. Project Structure

```
EmpSphere/
├── backend/
│   ├── config/                  # Django settings + root URL config
│   ├── apps/
│   │   ├── authentication/      # Auth controllers/services/repos/serializers/managers
│   │   ├── organization/        # (Week 2) Department/Designation/Employee
│   │   ├── activity_logs/       # Audit logging service
│   │   └── common/              # Shared base classes, security, responses, RBAC, middleware
│   ├── manage.py
│   ├── requirements.txt
│   └── logs/                    # Runtime log files
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI (Button, Input, Avatar, Layout, Dashboard, ...)
│   │   ├── config/              # Axios instance + environment config
│   │   ├── hooks/               # useAuth
│   │   ├── pages/               # Screens (auth, dashboards, errors)
│   │   ├── routes/              # AppRoutes + ProtectedRoute + DashboardRedirect
│   │   ├── services/            # API service wrappers (auth, user)
│   │   ├── store/               # Redux Toolkit store + slices + middleware
│   │   ├── styles/              # Tailwind globals
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Token storage, constants, helpers
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── postman/                     # Postman collection JSON
├── CODEBASE_EXPLAINED.md        # Plain-English guide to the whole codebase
├── FILE_REFERENCE.md            # Complete per-file reference
└── README.md                    # This file
```

---

## 5. Architecture Overview

The backend follows a **layered architecture**:

| Layer | Folder | Responsibility |
|-------|--------|----------------|
| Controller | `controllers/` | Receive HTTP requests, validate via serializers, return responses |
| DTO | `dtos/` | Typed data containers passed to services |
| Service | `services/` | Business logic (validations, orchestrating repositories) |
| Repository | `repositories/` | Direct MongoDB data access (built on `BaseRepository`) |
| Schema | `schemas/` | Document shape builders for MongoDB |
| Serializer | `serializers/` | DRF request validation |
| Validator | `validators/` | Domain-level business rules |
| Manager | `managers/` | Reusable helpers (JWT, password, email, blacklist) |

**Request flow example (Login):**

1. `LoginController.post()` receives email + password.
2. `LoginSerializer` validates the payload.
3. Data is wrapped in a `LoginDTO`.
4. `LoginService.login()` looks up the user, verifies the password, checks the account, and issues JWT access + refresh tokens.
5. The controller returns a standardized `{ success, message, data }` response.

All responses use a consistent envelope built by `apps/common/responses/api_response.py`, and all exceptions are normalized by `apps/common/exceptions/exception_handler.py`.

**MongoDB access** is centralized in `apps/common/database/mongo.py` (a singleton connection) with collection names in `apps/common/core/collections.py`.

---

## 6. How to Run

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB running locally (`mongodb://localhost:27017`) — or set `MONGO_URI` in the backend `.env`

### 6.1 Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# Create a .env file with the required keys
# Minimum for local dev:
#   MONGO_URI=mongodb://localhost:27017
#   DATABASE_NAME=empsphere_db
#   JWT_SECRET=<a-long-random-string>
#   SECRET_KEY=<a-long-random-string>

python manage.py check          # verify configuration
python manage.py seed_rbac      # seed roles + default Super Admin
python manage.py runserver 8000
```

The API will be available at `http://127.0.0.1:8000/api`.

> Default seeded Super Admin: `admin@empsphere.com` / `Admin@12345`
> (You can override with `--email` and `--password` flags on `seed_rbac`.)

### 6.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

The frontend reads `VITE_API_BASE_URL` from `frontend/.env` (defaults to `http://127.0.0.1:8000/api`).

### 6.3 API Endpoints (Week 1)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Create an account | Public |
| POST | `/api/auth/login/` | Log in, get tokens | Public |
| POST | `/api/auth/logout/` | Revoke refresh token | Bearer |
| GET | `/api/auth/me/` | Current user profile | Bearer |
| POST | `/api/auth/refresh-token/` | Get a new access token | Public |
| POST | `/api/auth/change-password/` | Change password | Bearer |
| POST | `/api/auth/forgot-password/` | Request reset link | Public |
| POST | `/api/auth/reset-password/` | Reset password | Public |
| POST | `/api/auth/verify-email/` | Verify email | Public |
| POST | `/api/auth/google-login/` | Google OAuth login (optional) | Public |

### 6.4 Role-Based Dashboard Routes

| Role | Dashboard path |
|------|----------------|
| SUPER_ADMIN | `/dashboard/super-admin` |
| ADMIN | `/dashboard/admin` |
| HR_MANAGER | `/dashboard/hr` |
| EMPLOYEE | `/dashboard/employee` |

---

## 7. Postman Collection

1. Open Postman → **Import** → select `postman/EmpSphere_Week1.postman_collection.json`.
2. Run **Login** to capture `accessToken`/`refreshToken` into collection variables.
3. Use the captured token for `me`, `logout`, and `change-password` requests.

---

## 8. Documentation

- `README.md` — Quick start + project overview (this file).
- `CODEBASE_EXPLAINED.md` — Plain-English explanation of the whole project.
- `FILE_REFERENCE.md` — Complete per-file reference (backend + frontend, every file explained).

---

## 9. Common Commands

```bash
# Backend checks
cd backend
python manage.py check

# Frontend type-check + build
cd frontend
npx tsc --noEmit
npm run build
```
</content>
