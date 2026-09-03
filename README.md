# EmpSphere

Full-stack Employee Management System with role-based access control, attendance tracking, leave management, and office payment processing via Razorpay.

## Features

- JWT authentication with refresh token rotation
- RBAC: SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE
- Employee and department management
- Attendance check-in / check-out
- Leave application and approval workflow
- Office amenity payments via Razorpay (Test Mode)
- Activity logging and audit trails
- Role-specific dashboard and reports

## Tech Stack

**Backend:** Django 4.2, Django REST Framework, PyMongo, PyJWT, python-dotenv  
**Frontend:** React 18, TypeScript, Vite 5, Redux Toolkit, Tailwind CSS, Axios  
**Database:** MongoDB (business data), SQLite in-memory (Django internal tables)  
**Payments:** Razorpay (Test Mode) — only payment gateway, no gateway selector

## Quick Start

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create backend/.env (see docs/PROJECT_GUIDE.md)
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

## Verify

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check

cd ..\frontend
npx tsc --noEmit
npm run build
```

## Documentation

See [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) for a beginner-friendly walkthrough of the entire system.
