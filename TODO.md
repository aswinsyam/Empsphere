# EmpSphere — Week 1 Completion Checklist

## Backend
- [x] Audit existing project (backend + frontend)
- [x] Fix public registration role security (force EMPLOYEE)
- [x] Add refresh-token rotation (blacklist old refresh on refresh)
- [x] Add jti to JWT payload
- [x] Make token blacklist jti-based, duplicate-safe, TTL-aware
- [x] Add reusable RBAC helpers (can_manage_user, can_assign_role, owns_resource, can_manage_employee)
- [x] Refactor CreateUserService to use centralized can_assign_role helper
- [x] Add Profile Update (PATCH) endpoint + service + DTO + serializer
- [x] Add Profile Image Upload endpoint + service
- [x] Register profile routes in urls.py

## Frontend
- [x] Fix axios refresh interceptor to store BOTH new access + refresh tokens
- [x] Clear Redux auth + redirect on refresh failure
- [x] Add role-aware route protection (RequireRole)
- [x] Wrap role dashboards with RequireRole in AppRoutes
- [x] Add /profile route
- [x] Fix Navbar dropdown (add View Profile, fix z-index/overflow/positioning)
- [x] Create Profile page + profile components
- [x] Add updateProfile + uploadProfileImage services
- [x] Add googleLogin service + "Continue with Google" button on LoginPage
- [x] Add Confirm Password field to ResetPasswordForm
- [x] Handle logoutUser.rejected in authSlice (clear stale state)

## Verification
- [x] Backend: python compileall + manage.py check (PASSED)
- [x] Frontend: npx tsc --noEmit + npm run build (PASSED)
- [x] Test auth flows (register, login, me, refresh, logout, RBAC, profile)
