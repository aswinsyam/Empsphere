# EmpSphere — Employee Management System

**EmpSphere** is a full-stack Employee Management System built with Django REST Framework (backend) and React + TypeScript (frontend). It provides role-based dashboards, attendance tracking, leave management, employee records, activity logging, and reporting—all secured with JWT authentication and RBAC.

---

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Runs the Django backend |
| Node.js | 18+ | Runs the Vite frontend |
| npm | 9+ | Installs frontend dependencies |
| MongoDB | 6.0+ | Database for all application data |
| Git | Any | Clone the repository |

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Django 4.2 | Python web framework — project structure, URL routing, middleware |
| Django REST Framework | Turns Django into a REST API server — serialization, auth, permissions |
| PyMongo | MongoDB driver for Python |
| GridFS | Stores large files (profile images) in MongoDB |
| PyJWT | Creates and verifies JSON Web Tokens for login sessions |
| python-dotenv | Loads secrets from `.env` so keys are never hardcoded |

### Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | UI library — renders interactive components |
| TypeScript | Static typing for JavaScript |
| Vite 5 | Build tool and dev server |
| Redux Toolkit | Predictable state container — stores auth, employee lists, etc. |
| Tailwind CSS | Utility-first CSS framework |
| React Router 7 | Client-side navigation |
| Axios | HTTP client for API calls |

---

## Project Structure

```
EmpSphere/
├── backend/                 # Django REST API
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py      # Django settings, DRF config, JWT, email, logging
│   │   └── urls.py          # Root URL router
│   ├── apps/
│   │   ├── common/          # Shared utilities (base classes, security, middleware, etc.)
│   │   ├── authentication/  # Login, register, OTP, password reset, profile, Google auth
│   │   ├── organization/    # Departments and designations
│   │   ├── employee/        # Employee CRUD
│   │   ├── attendance/      # Attendance marking, check-in/out, summaries
│   │   ├── leave/           # Leave apply, approve/reject
│   │   ├── activity_logs/   # Activity log retrieval
│   │   ├── statistics/      # Dashboard statistics
│   │   └── reports/         # Report generation
│   ├── templates/
│   └── requirements.txt
├── frontend/                # React + Vite web app
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-level components
│   │   ├── services/        # API service functions
│   │   ├── store/           # Redux slices and middleware
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript interfaces
│   │   ├── utils/           # Helper functions
│   │   ├── config/          # Axios instance and environment config
│   │   ├── routes/          # Route definitions and guards
│   │   └── styles/          # Global CSS
│   ├── package.json
│   └── vite.config.ts
└── docs/                    # Documentation (this folder)
```

---

## Architecture

### Backend: Controller → Service → Repository → MongoDB

```
HTTP Request
    ↓
Controller (APIView)
    ↓  validates input via Serializer
Service
    ↓  contains business logic
Repository
    ↓  talks to MongoDB
MongoDB
    ↓
Response via ApiResponse
```

### Frontend: Page → Hook → Service → Axios → Backend

```
Page Component
    ↓  uses custom Hook
Hook (useDispatch/useSelector + thunks)
    ↓  calls Service
Service (Axios instance)
    ↓  HTTP request
Backend API
```

---

## Key Concepts

### Authentication
- JWT access tokens (30 min) and refresh tokens (7 days)
- Refresh token rotation with blacklisting
- Email verification via OTP
- Google OAuth2 login

### Authorization (RBAC)
- Four roles: EMPLOYEE, HR_MANAGER, ADMIN, SUPER_ADMIN
- Role hierarchy enforced via `RolePermission`
- `@require_role` decorator on controller methods

### OTP System
- Centralized `OTPPurpose` enum: email_verification, login, first_login, password_setup, forgot_password
- OTPs stored in MongoDB with expiry and single-use enforcement
- Email delivery via Django SMTP

### MongoDB & GridFS
- All data stored in MongoDB collections
- Profile images stored in GridFS with user reference
- Collection names centralized in `Collections` enum

### Activity Logging
- `BaseService.log_activity()` inherited by all services
- Writes to `activity_logs` collection
- Tracks module, action, performer, target, status, description

---

## Where to Start Learning the Code

1. **Backend**: Start with `config/settings.py` → `config/urls.py` → `apps/authentication/views/auth_view.py` → `apps/authentication/services/auth_service.py`
2. **Frontend**: Start with `src/main.tsx` → `src/App.tsx` → `src/routes/AppRoutes.tsx` → `src/pages/dashboard/`
3. **Common utilities**: `apps/common/base/` and `src/utils/` are the best places to understand shared patterns

---

## Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — Detailed explanation of every folder
- [FILE_BY_FILE_GUIDE.md](FILE_BY_FILE_GUIDE.md) — Purpose and implementation of every important file
- [CODE_EXPLANATION.md](CODE_EXPLANATION.md) — Line-by-line explanation of complex code blocks
