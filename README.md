# EmpSphere

Full-stack Employee Management System with role-based access control, attendance tracking, leave management, and office payment processing via Cashfree.

## Features

- JWT authentication with refresh token rotation
- RBAC: SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE
- Employee and department management
- Attendance check-in / check-out
- Leave application and approval workflow
- Office amenity payments via Cashfree Sandbox
- Activity logging and audit trails
- Role-specific dashboard and reports

## Tech Stack

**Backend:** Django 4.2, Django REST Framework, PyMongo, PyJWT, python-dotenv  
**Frontend:** React 18, TypeScript, Vite 5, Redux Toolkit, Tailwind CSS, Axios  
**Database:** MongoDB (business data), SQLite in-memory (Django internal tables)  
**Payments:** Cashfree

## Architecture

**Backend:** HTTP Request → Controller → Service → Repository → MongoDB  
**Frontend:** Page → Hook → Redux Slice → Service → Axios → Backend API

## Quick Start

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create backend/.env (see docs/PROJECT_GUIDE.md §18)
.\venv\Scripts\python.exe manage.py seed_rbac
.\venv\Scripts\python.exe manage.py seed_amenities
.\venv\Scripts\python.exe manage.py runserver

# Frontend
cd frontend
npm install
# Copy frontend/.env.example to frontend/.env
npm run dev
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## Environment Setup

All `.env` files are gitignored. The repository has no committed `.env`.

- **Backend:** `backend/.env` — secrets, MongoDB URI, email SMTP, Cashfree credentials.
- **Frontend:** `frontend/.env` — API base URL, Google OAuth client ID.

Copy `frontend/.env.example` to `frontend/.env` and fill in the values.

## Cashfree Sandbox

Payments run in **SANDBOX** mode by default (`CASHFREE_ENVIRONMENT=SANDBOX` in `backend/.env`). Get sandbox test credentials from the Cashfree Dashboard → Sandbox → API Credentials. Switch `CASHFREE_ENVIRONMENT` to `PRODUCTION` only when deploying live.

> **Important:** `CASHFREE_SECRET_KEY` is backend-only. Never place it in frontend code, README, or logs.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) | Complete project guide for beginners |
