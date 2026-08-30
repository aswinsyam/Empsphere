# EmpSphere Developer Guide

## 1. What is EmpSphere?

EmpSphere is a full-stack Employee Management System (EMS) built with Django REST Framework and React. It provides role-based access control (RBAC) for managing employees, departments, attendance, leaves, and office payments.

**Key Features:**
- JWT-based authentication with refresh token rotation
- Role-based access control (SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE)
- Employee management with profile images stored in MongoDB GridFS
- Attendance tracking with check-in/check-out
- Leave management with approval workflow
- Office payment processing with Cashfree integration
- Activity logging for audit trails
- Dashboard with role-specific views

---

## 2. Complete Project Architecture

```
EmpSphere/
├── backend/                 # Django REST API
│   ├── config/              # Django project settings
│   ├── apps/                # Django applications
│   │   ├── authentication/  # Auth, users, profile images
│   │   ├── employee/        # Employee management
│   │   ├── organization/    # Departments & designations
│   │   ├── attendance/      # Attendance tracking
│   │   ├── leave/           # Leave management
│   │   ├── payment/         # Office payment with Cashfree
│   │   ├── activity_logs/   # Audit logging
│   │   ├── statistics/      # Dashboard statistics
│   │   ├── reports/         # Reporting module
│   │   └── common/          # Shared infrastructure
│   ├── templates/           # Email templates
│   └── manage.py            # Django CLI
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service layer
│   │   ├── store/           # Redux store
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Utilities & constants
│   │   ├── routes/          # Route configuration
│   │   └── config/          # App configuration
│   └── package.json
└── docs/                    # Documentation
```

---

## 3. Backend Folder Structure

### `backend/config/`
- `settings.py` - Django settings (INSTALLED_APPS, MIDDLEWARE, DRF config, JWT settings)
- `urls.py` - Root URL router mounting all app URLs under `/api/`

### `backend/apps/common/`
Shared infrastructure used by all apps:
- `core/roles.py` - Role enum (EMPLOYEE=1, HR_MANAGER=2, ADMIN=3, SUPER_ADMIN=4)
- `core/permissions.py` - Permission constants and ROLE_PERMISSIONS mapping
- `core/otp.py` - OTP purpose constants (EMAIL_VERIFICATION, FORGOT_PASSWORD, etc.)
- `core/collections.py` - MongoDB collection name constants
- `security/password_manager.py` - bcrypt password hashing
- `responses/api_response.py` - Standardized API response builder
- `base/base_service.py` - Base service with audit logging
- `base/base_controller.py` - Base controller with response helpers
- `exceptions/custom_exception.py` - Custom exceptions (ValidationException, NotFoundException, etc.)
- `middleware/authentication.py` - JWT authentication middleware
- `database/mongo.py` - MongoDB connection singleton
- `decorators/permission.py` - @require_role decorator
- `permissions/role_permission.py` - Role hierarchy helpers

### `backend/apps/authentication/`
Authentication and user management:
- `views/auth_view.py` - Register, login, logout endpoints
- `views/otp_view.py` - OTP send/verify endpoints
- `views/password_view.py` - Change/set/forgot/reset password
- `views/user_view.py` - User profile, profile image upload
- `services/auth_service.py` - Authentication business logic
- `services/otp_service.py` - OTP generation and email delivery
- `services/password_service.py` - Password operations
- `services/profile_image_service.py` - GridFS image storage
- `repositories/user_repository.py` - User data access
- `repositories/otp_repository.py` - OTP data access
- `managers/token_blacklist_manager.py` - JWT blacklisting
- `managers/password_reset_token_manager.py` - Reset token management
- `managers/employee_code_manager.py` - Employee code generation

### `backend/apps/employee/`
Employee management:
- `controllers/employee_controller.py` - Employee CRUD endpoints
- `services/employee_service.py` - Employee business logic
- `repositories/employee_repository.py` - Employee data access
- `validators/employee_validator.py` - Employee validation

### `backend/apps/organization/`
Departments and designations:
- `controllers/department_controller.py` - Department CRUD
- `controllers/designation_controller.py` - Designation CRUD
- `services/department_service.py` - Department business logic
- `services/designation_service.py` - Designation business logic
- `repositories/department_repository.py` - Department data access
- `repositories/designation_repository.py` - Designation data access

### `backend/apps/attendance/`
Attendance tracking:
- `controllers/attendance_controller.py` - Check-in/check-out, marking
- `services/attendance_service.py` - Attendance business logic
- `repositories/attendance_repository.py` - Attendance data access

### `backend/apps/leave/`
Leave management:
- `controllers/leave_controller.py` - Apply, approve, reject
- `services/leave_service.py` - Leave business logic
- `repositories/leave_repository.py` - Leave data access

### `backend/apps/payment/`
Office payment processing with Cashfree:
- `controllers/payment_controller.py` - Create, verify, cancel payments
- `services/payment_service.py` - Payment business logic with Cashfree
- `repositories/payment_repository.py` - Payment data access
- `gateways/cashfree_gateway.py` - Cashfree integration
- `dtos/payment_dto.py` - Data transfer objects
- `serializers/payment_serializer.py` - Request validation
- `validators/payment_validator.py` - Business validation
- `amenities/amenity_controller.py` - Amenity CRUD endpoints
- `amenities/amenity_service.py` - Amenity business logic
- `amenities/amenity_repository.py` - Amenity data access
- `amenities/amenity_dto.py` - Amenity data transfer objects
- `amenities/amenity_serializer.py` - Amenity request validation

### `backend/apps/activity_logs/`
Audit logging:
- `views/activity_log_view.py` - List activity logs
- `services/audit_service.py` - Write audit records

---

## 4. Frontend Folder Structure

### `frontend/src/config/`
- `axios.ts` - Axios instance with interceptors (token refresh on 401)
- `env.ts` - Environment variable access

### `frontend/src/store/`
Redux Toolkit store:
- `index.ts` - Store configuration
- `slices/authSlice.ts` - Authentication state
- `slices/employeeSlice.ts` - Employee state
- `slices/departmentSlice.ts` - Department state
- `slices/attendanceSlice.ts` - Attendance state
- `slices/leaveSlice.ts` - Leave state
- `slices/paymentSlice.ts` - Office payment state

### `frontend/src/services/`
API service layer:
- `api.ts` - Base HTTP client
- `auth.service.ts` - Authentication API calls
- `employee.service.ts` - Employee API calls
- `department.service.ts` - Department API calls
- `attendance.service.ts` - Attendance API calls
- `leave.service.ts` - Leave API calls
- `payment.service.ts` - Office payment API calls
- `activityLog.service.ts` - Activity log API calls

### `frontend/src/hooks/`
Custom React hooks:
- `useAuth.ts` - Authentication state and actions
- `useEmployees.ts` - Employee list and actions
- `useDepartments.ts` - Department list and actions
- `useAttendance.ts` - Attendance records and actions
- `useLeaves.ts` - Leave records and actions
- `usePayment.ts` - Office payment records and actions
- `useDashboardData.ts` - Dashboard data loading

### `frontend/src/components/`
Reusable UI components:
- `common/Pagination.tsx` - Pagination controls
- `common/StatusBadge.tsx` - Status indicator badge
common/Modal.tsx` - Modal dialog
- `common/Button.tsx` - Button component
- `common/Input.tsx` - Form input component
- `common/Loader.tsx` - Loading spinner
- `common/PageHeader.tsx` - Page header with actions
- `layout/Sidebar.tsx` - Sidebar navigation
- `layout/Navbar.tsx` - Top navigation bar
- `layout/DashboardLayout.tsx` - Dashboard layout wrapper

### `frontend/src/pages/`
Page components organized by feature:
- `auth/` - Login, Register, VerifyEmail, ForgotPassword, etc.
- `dashboard/` - Role-specific dashboards
- `employees/` - Employee list and detail
- `departments/` - Department list and detail
- `attendance/` - Attendance management
- `leaves/` - Leave management
- `payroll/` - Payroll management
- `payments/` - Payment management
- `activityLogs/` - Activity log viewer
- `reports/` - Report generation
- `profile/` - User profile

---

## 5. What Every Folder Does

### Backend Apps

| Folder | Purpose |
|--------|---------|
| `authentication/` | User registration, login, logout, OTP, password management, profile images |
| `employee/` | Employee CRUD operations, role assignment |
| `organization/` | Department and designation management |
| `attendance/` | Employee check-in/check-out, attendance marking |
| `leave/` | Leave application, approval, rejection |
| `payment/` | Office payment processing with Cashfree |
| `activity_logs/` | Audit trail for all system actions |
| `statistics/` | Dashboard statistics aggregation |
| `reports/` | Report generation for all modules |
| `common/` | Shared infrastructure (auth, responses, exceptions, etc.) |

### Frontend Folders

| Folder | Purpose |
|--------|---------|
| `components/` | Reusable UI components |
| `pages/` | Page-level components |
| `hooks/` | Custom hooks wrapping Redux actions |
| `services/` | API call functions |
| `store/` | Redux store and slices |
| `types/` | TypeScript type definitions |
| `utils/` | Utility functions and constants |
| `routes/` | Route configuration and guards |
| `config/` | App configuration |

---

## 6. What Every Important File Does

### Backend Core Files

**`apps/common/core/roles.py`**
- Defines the Role enum (EMPLOYEE=1 through SUPER_ADMIN=4)
- Provides role group constants (MANAGEMENT_ROLES, EMPLOYEE_MANAGER_ROLES)
- Helper functions: `has_role()`, `is_super_admin()`, `is_admin()`, etc.

**`apps/common/core/permissions.py`**
- Defines all permission strings (PERM_LOGIN, PERM_EMPLOYEE_CREATE, etc.)
- Maps permissions to roles via ROLE_PERMISSIONS dict
- Functions: `roles_for_permission()`, `has_permission()`

**`apps/common/responses/api_response.py`**
- Standardized API response builder
- Methods: `success()`, `error()`, `paginated()`

**`apps/common/base/base_service.py`**
- Base class for all services
- Provides `log_activity()` method for audit logging

**`apps/common/base/base_controller.py`**
- Base class for all controllers
- Provides `success()` and `error()` response helpers

**`apps/common/exceptions/custom_exception.py`**
- Custom exceptions: ValidationException, UnauthorizedException, ForbiddenException, NotFoundException, ConflictException, InternalServerException

**`apps/common/middleware/authentication.py`**
- JWT authentication middleware
- Decodes JWT and attaches user dict to request

**`apps/common/database/mongo.py`**
- MongoDB connection singleton
- Provides `get_collection()` method

**`apps/common/decorators/permission.py`**
- `@require_role(*allowed_roles)` decorator
- Enforces role-based access on controller methods

### Authentication Files

**`authentication/services/auth_service.py`**
- `register()` - Creates admin user with company secret validation
- `login()` - Authenticates user, returns tokens or triggers OTP
- `verify_first_login()` - Verifies first-login OTP and issues tokens
- `refresh_token()` - Rotates refresh token and issues new access token
- `_generate_access_token()` - Creates JWT access token
- `_generate_refresh_token()` - Creates JWT refresh token

**`authentication/services/otp_service.py`**
- `send_otp()` - Generates OTP, stores in MongoDB, sends email
- `verify_otp()` - Validates OTP code for email+purpose
- `_generate_otp()` - Cryptographically secure 6-digit OTP

**`authentication/services/profile_image_service.py`**
- `upload()` - Stores image in GridFS, updates user's profile_image_id
- `get()` - Retrieves image from GridFS by file_id
- `delete()` - Removes image from GridFS
- Validates file type (JPEG, PNG, WebP, GIF) and size (5MB max)

**`authentication/views/user_view.py`**
- `UserView` - GET/PATCH user profile
- `ProfileImageView` - POST profile image upload
- `serve_profile_image()` - Public endpoint to serve profile images from GridFS

---

## 7. Authentication Complete Flow

### Register
```
User → POST /api/auth/register/
    → AuthView._register()
    → AuthService.register()
    → Validates company_secret
    → Generates employee_code
    → Hashes password with bcrypt
    → Creates user document in MongoDB
    → Sends email verification OTP
    → Returns user_id
```

### Login
```
User → POST /api/auth/login/
    → AuthView._login()
    → AuthService.login()
    → Verifies email + password
    → If email not verified: returns requires_otp=true
    → If verified: generates JWT access + refresh tokens
    → Updates last_login
    → Logs LOGIN activity
    → Returns tokens + user data
```

### OTP Verification
```
User → POST /api/auth/verify-otp/
    → OTPView.post()
    → OTPService.verify_otp()
    → Validates OTP for email+purpose
    → Marks OTP as used
    → For FIRST_LOGIN: issues tokens
    → For EMAIL_VERIFICATION: marks email verified, issues tokens
    → For FORGOT_PASSWORD: returns reset_token
```

### Refresh Token
```
Frontend (on 401) → POST /api/auth/refresh-token/
    → AuthService.refresh_token()
    → Validates refresh token
    → Blacklists old refresh token
    → Issues new access + refresh tokens
```

### Logout
```
User → POST /api/auth/logout/
    → AuthView._logout()
    → Blacklists refresh token
    → Logs LOGOUT activity
    → Frontend clears tokens from localStorage
```

### Forgot Password
```
User → POST /api/auth/forgot-password/
    → PasswordView._forgot_password()
    → PasswordService.request_password_reset()
    → If account exists: sends FORGOT_PASSWORD OTP
    → Always returns same message (no account enumeration)

User → POST /api/auth/verify-otp/ (purpose=FORGOT_PASSWORD)
    → PasswordService.verify_password_reset_otp()
    → Verifies OTP
    → Issues single-use reset_token

User → POST /api/auth/reset-password/
    → PasswordService.reset_password()
    → Validates reset_token
    → Hashes new password
    → Invalidates reset_token
    → Blacklists all user tokens
```

---

## 8. Profile Image Complete Flow

### Storage Architecture

MongoDB does NOT store the image as normal JSON in the users collection. Instead:

1. **users collection** stores only a reference: `profile_image_id` (ObjectId)
2. **GridFS** stores the actual binary data in two collections:
   - `fs.files` - File metadata (filename, content_type, uploadDate)
   - `fs.chunks` - Binary chunks of the file

### Upload Flow
```
React FormData → POST /api/auth/profile/image/
    → ProfileImageView.post()
    → ProfileImageService.upload()
    → Validates file type and size
    → Deletes old GridFS file if exists
    → Stores new file in GridFS via gridfs.put()
    → Updates user's profile_image_id in users collection
    → Returns updated user data
```

### Retrieval Flow
```
Browser <img> tag → GET /api/auth/profile/image/<user_id>/
    → serve_profile_image()
    → Looks up user by user_id
    → Gets profile_image_id from user document
    → Retrieves file from GridFS via gridfs.get()
    → Returns binary data with Content-Type header
```

### Key Points
- Profile images are served publicly (no JWT required) because the URL contains the non-guessable ObjectId
- Cache headers prevent stale images
- Old images are deleted when replaced
- Supported formats: JPEG, PNG, WebP, GIF (max 5MB)

---

## 9. Employee Flow

### Create Employee
```
Admin → POST /api/employees/
    → EmployeeController.post() [@require_role(EMPLOYEE_MANAGER_ROLES)]
    → EmployeeService.create_employee()
    → Validates input
    → Checks email uniqueness
    → Hashes password
    → Creates user document with role
    → Logs CREATE_EMPLOYEE activity
```

### List Employees
```
Admin → GET /api/employees/?page=1&page_size=10&search=&status=&department_id=
    → EmployeeController.get()
    → EmployeeService.list_employees()
    → EmployeeRepository.get_all()
    → Builds MongoDB query from filters
    → Returns paginated results with total_records, total_pages
```

### Update Employee
```
Admin → PUT /api/employees/<id>/
    → EmployeeController.put()
    → EmployeeService.update_employee()
    → Validates update data
    → Checks role hierarchy (can_manage_user)
    → Updates employee document
    → Logs UPDATE_EMPLOYEE activity
```

### Activate/Deactivate
```
Admin → PATCH /api/employees/<id>/ {status: "INACTIVE"}
    → EmployeeController.patch()
    → EmployeeService.update_employee_status()
    → Validates status
    → Updates status field
    → Logs ACTIVATE/DEACTIVATE_EMPLOYEE activity
```

---

## 10. Department Flow

### Create Department
```
Admin → POST /api/organization/departments/
    → DepartmentController.post()
    → DepartmentService.create_department()
    → Validates name/code uniqueness
    → Creates department document
    → Logs CREATE_DEPARTMENT activity
```

### List Departments
```
Admin → GET /api/organization/departments/?page=1&search=&include_inactive=true
    → DepartmentController.get()
    → DepartmentService.list_departments()
    → DepartmentRepository.get_all()
    → Returns paginated results
```

### Department Members
```
Admin → GET /api/employees/?department_id=<id>
    → Filters employees by department_id
    → Returns employees in that department
```

---

## 11. Attendance Flow

### Employee Check-In
```
Employee → POST /api/attendance/check-in/
    → AttendanceController._check_in()
    → AttendanceService.check_in()
    → Verifies employee is active
    → Checks for existing attendance today
    → If no record: creates new with server timestamp
    → If record without check_in: updates check_in timestamp
    → Prevents duplicate check-in
    → Logs CHECK_IN activity
```

### Employee Check-Out
```
Employee → POST /api/attendance/check-out/
    → AttendanceController._check_out()
    → AttendanceService.check_out()
    → Verifies employee is active
    → Finds today's attendance record
    → Verifies check-in exists
    → Prevents duplicate check-out
    → Updates check_out with server timestamp
    → Logs CHECK_OUT activity
```

### Admin Mark Attendance
```
Admin → POST /api/attendance/ {employee_id, date, status, check_in, check_out}
    → AttendanceController._mark_attendance()
    → AttendanceService.mark_attendance()
    → Validates employee is active
    → Prevents duplicate attendance for date
    → Creates attendance record
    → Logs CREATE_ATTENDANCE activity
```

### Key Business Rules
- Server determines timestamps for employee self check-in/check-out
- Employees cannot enter arbitrary dates/times
- Duplicate check-in/check-out prevented
- MongoDB unique index on (employee_id, date) prevents duplicates

---

## 12. Leave Flow

### Apply Leave
```
Employee → POST /api/leaves/ {start_date, end_date, leave_type, reason}
    → LeaveController.post()
    → LeaveService.apply_leave()
    → Validates dates (start <= end)
    → Validates leave_type
    → Verifies employee is active
    → Creates leave with PENDING status
    → Logs APPLY_LEAVE activity
```

### Approve/Reject Leave
```
Admin → PUT /api/leaves/<id>/ {status: "APPROVED"}
    → LeaveController.put() [@require_role(HR_MANAGER, ADMIN, SUPER_ADMIN)]
    → LeaveService.update_leave_status()
    → Validates leave is PENDING
    → Prevents self-approval
    → Updates status and approved_by/rejected_by
    → Logs APPROVE_LEAVE/REJECT_LEAVE activity
```

---

## 13. Office Payment Flow

### Create Payment
```
Employee → POST /api/payment/ {title, description, category, amount}
    → PaymentController.post()
    → PaymentService.create_payment()
    → Validates input
    → Creates Cashfree order
    → Creates payment record with PENDING status
    → Returns order details for frontend
```

### Verify Payment
```
Employee → Frontend Cashfree Checkout → Payment callback
    → POST /api/payment/<id>/verify/ {gateway_order_id, gateway_payment_id, payment_status}
    → PaymentController (verify)
    → PaymentService.verify_payment()
    → Verifies payment status with Cashfree API
    → Updates payment to PAID status
    → Logs PAYMENT_VERIFIED activity
```

### Cancel Payment
```
Employee → POST /api/payment/<id>/cancel/
    → PaymentController (cancel)
    → PaymentService.cancel_payment()
    → Validates status (not PAID or CANCELLED)
    → Updates to CANCELLED
    → Logs PAYMENT_CANCELLED activity
```

### Cashfree Integration
```
Frontend → Backend → Cashfree Order API
    ↓
Returns order information
    ↓
Frontend opens Cashfree Checkout
    ↓
Employee completes payment
    ↓
Cashfree returns payment details
    ↓
Frontend sends verification data
    ↓
Backend verifies payment status with Cashfree API
    ↓
Updates MongoDB payment
    ↓
Activity Log
    ↓
Returns success
```

**Security Notes:**
- Never trust amount, status, or transaction_id from frontend
- Cashfree payment status must be verified on backend via API
- Cashfree secret must remain backend-only
- Frontend only receives payment session ID for checkout

---

## 14. RBAC Role Matrix

| Feature | SUPER_ADMIN | ADMIN | HR_MANAGER | EMPLOYEE |
|---------|-------------|-------|------------|----------|
| **Authentication** |
| Login | ✅ | ✅ | ✅ | ✅ |
| Register Admin | ✅ | ✅ | ❌ | ❌ |
| Manage Profile | ✅ | ✅ | ✅ | ✅ |
| **Employees** |
| Create | ✅ | ✅ | ✅ | ❌ |
| View All | ✅ | ✅ | ✅ | ❌ |
| Update | ✅ | ✅ | ✅ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |
| **Departments** |
| Create | ✅ | ✅ | ✅ | ❌ |
| View | ✅ | ✅ | ✅ | ❌ |
| Update | ✅ | ✅ | ✅ | ❌ |
| Delete | ✅ | ✅ | ✅ | ❌ |
| **Attendance** |
| Mark Own | ✅ | ✅ | ✅ | ✅ |
| Mark Others | ✅ | ✅ | ✅ | ❌ |
| View All | ✅ | ✅ | ✅ | ❌ |
| View Own | ✅ | ✅ | ✅ | ✅ |
| Update | ✅ | ✅ | ✅ | ❌ |
| **Leave** |
| Apply | ✅ | ✅ | ✅ | ✅ |
| Approve/Reject | ✅ | ✅ | ✅ | ❌ |
| View All | ✅ | ✅ | ✅ | ❌ |
| View Own | ✅ | ✅ | ✅ | ✅ |
| **Payment** |
| Create | ✅ | ✅ | ✅ | ✅ |
| View All | ✅ | ✅ | ✅ | ❌ |
| View Own | ✅ | ✅ | ✅ | ✅ |
| Verify | Backend | Backend | Backend | Backend |
| **Reports** |
| View | ✅ | ✅ | ✅ | ❌ |
| Export | ✅ | ✅ | ✅ | ❌ |
| **Activity Logs** |
| View | ✅ | ✅ | ✅ | ✅ (own) |

---

## 16. MongoDB Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `users` | Employee/user accounts | employee_code, email, password, role, department_id, designation_id, profile_image_id, status |
| `departments` | Department records | name, code, description, head_user_id, is_active |
| `designations` | Job designations | name, code, description, is_active |
| `attendance` | Attendance records | employee_id, date, status, check_in, check_out |
| `leaves` | Leave applications | employee_id, start_date, end_date, leave_type, status |
| `payments` | Office payment records | employee_id, title, category, amount, status, transaction_id |
| `activity_logs` | Audit trail | module, action, performed_by, target_id, status, description |
| `otps` | OTP codes | email, purpose, otp, expires_at, is_used |
| `tokens` | Blacklisted tokens | token, user_id, blacklisted_at |
| `fs.files` | GridFS file metadata | filename, content_type, uploadDate, metadata |
| `fs.chunks` | GridFS binary chunks | files_id, n, data |

### Indexes
- `users`: email (unique), employee_code (unique)
- `departments`: name (unique), code (unique)
- `designations`: name (unique), code (unique)
- `attendance`: (employee_id, date) unique
- `payments`: (employee_id, status), created_at, transaction_id
- `otps`: (email, purpose, is_used)

---

## 17. API Endpoint Documentation

### Authentication Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | Public | Register admin account |
| POST | `/api/auth/login/` | Public | Login, get tokens |
| POST | `/api/auth/logout/` | Authenticated | Blacklist refresh token |
| POST | `/api/auth/refresh-token/` | Public | Rotate tokens |
| GET | `/api/auth/me/` | Authenticated | Get current user profile |
| PATCH | `/api/auth/profile/` | Authenticated | Update profile |
| POST | `/api/auth/profile/image/` | Authenticated | Upload profile image |
| GET | `/api/auth/profile/image/<user_id>/` | Public | Serve profile image |
| POST | `/api/auth/send-otp/` | Public | Send OTP |
| POST | `/api/auth/verify-otp/` | Public | Verify OTP |
| POST | `/api/auth/change-password/` | Authenticated | Change password |
| POST | `/api/auth/forgot-password/` | Public | Request password reset |
| POST | `/api/auth/reset-password/` | Public | Reset password with token |

### Employee Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| GET | `/api/employees/` | MANAGER | List employees |
| POST | `/api/employees/` | MANAGER | Create employee |
| GET | `/api/employees/<id>/` | MANAGER | Get employee |
| PUT | `/api/employees/<id>/` | MANAGER | Update employee |
| PATCH | `/api/employees/<id>/` | MANAGER | Update status |
| DELETE | `/api/employees/<id>/` | SUPER_ADMIN | Delete employee |

### Department Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| GET | `/api/organization/departments/` | MANAGER | List departments |
| POST | `/api/organization/departments/` | MANAGER | Create department |
| GET | `/api/organization/departments/<id>/` | MANAGER | Get department |
| PUT | `/api/organization/departments/<id>/` | MANAGER | Update department |
| DELETE | `/api/organization/departments/<id>/` | MANAGER | Delete department |

### Attendance Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/attendance/check-in/` | Any | Check in |
| POST | `/api/attendance/check-out/` | Any | Check out |
| POST | `/api/attendance/` | MANAGER | Mark attendance |
| GET | `/api/attendance/` | Any | List attendance |
| GET | `/api/attendance/<id>/` | Any | Get attendance |
| PUT | `/api/attendance/<id>/` | MANAGER | Update attendance |

### Leave Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/leaves/` | Any | Apply leave |
| GET | `/api/leaves/` | Any | List leaves |
| GET | `/api/leaves/<id>/` | Any | Get leave |
| PUT | `/api/leaves/<id>/` | MANAGER | Approve/reject |

### Payment Endpoints

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/payment/` | Any | Create office payment |
| GET | `/api/payment/` | Any | List payments |
| GET | `/api/payment/<id>/` | Any | Get payment |
| POST | `/api/payment/<id>/verify/` | Any | Verify payment |
| POST | `/api/payment/<id>/cancel/` | Any | Cancel payment |
| GET | `/api/payment/me/` | Any | Get my payments |

---

## 18. Frontend Data Flow

```
Page Component
    ↓
Custom Hook (useEmployees, useAttendance, etc.)
    ↓
Redux Slice (employeeSlice, attendanceSlice, etc.)
    ↓
Async Thunk (fetchEmployees, checkIn, etc.)
    ↓
Service Layer (employeeService, attendanceService)
    ↓
Axios HTTP Client (with token interceptor)
    ↓
Backend API Endpoint
    ↓
Controller → Service → Repository → MongoDB
    ↓
Response → Redux Store Update → UI Re-render
```

### Token Refresh Flow
```
API returns 401
    ↓
Axios interceptor catches error
    ↓
Attempts to refresh token via /api/auth/refresh-token/
    ↓
If successful: retries original request with new token
    ↓
If failed: redirects to /login
```

---

## 19. Pagination

### Backend Pagination
- Query params: `page` (1-based), `page_size`
- Response includes: `total_records`, `total_pages`, `page`, `page_size`
- MongoDB: `skip = (page - 1) * page_size`, `limit = page_size`

### Frontend Pagination
- `Pagination.tsx` component shows "Page X of Y (Z total)"
- Previous/Next buttons with disabled states
- Each page calls `list({ ...filters, page: nextPage })`

---

## 20. Filtering

### How Filters Travel Frontend → MongoDB

```
Frontend Filter State
    ↓
Hook calls list({ status: "ACTIVE", department_id: "..." })
    ↓
Redux thunk passes params to service
    ↓
Service calls API: GET /api/employees/?status=ACTIVE&department_id=...
    ↓
Controller extracts query_params
    ↓
Service builds filter dict
    ↓
Repository builds MongoDB query
    ↓
MongoDB find() with query
```

---

## 21. Activity Logs

Activity logging occurs in every service via `BaseService.log_activity()`:
- Writes to `activity_logs` collection
- Records: module, action, performed_by, target_id, status, description
- Used for: LOGIN, LOGOUT, CREATE_EMPLOYEE, UPDATE_EMPLOYEE, CHECK_IN, CHECK_OUT, APPLY_LEAVE, APPROVE_LEAVE, PAYMENT_CREATED, PAYMENT_VERIFIED, PAYMENT_FAILED, PAYMENT_CANCELLED, etc.

---

## 22. Error Handling

### Backend
- `CustomException` subclasses with specific HTTP status codes
- `ExceptionHandler` middleware catches unhandled exceptions
- All errors return: `{ success: false, message: "...", errors: {...} }`

### Frontend
- Axios interceptor catches errors
- Redux slices store error messages
- Components display errors from slice state
- Toast notifications for user feedback

---

## 23. Security

- **Password Hashing**: bcrypt via passlib
- **JWT**: HS256 with secret from env
- **Token Rotation**: Refresh tokens are single-use
- **Token Blacklist**: Blacklisted tokens stored in MongoDB
- **RBAC**: @require_role decorator on controllers
- **Employee Self-Isolation**: Backend filters by user_id for EMPLOYEE role
- **File Upload**: Type and size validation for profile images
- **CORS**: Configured via django-cors-headers
- **Payment Security**: Cashfree payment status verified on backend via API, secrets never exposed to frontend

---

## 24. How to Run the Project

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB 5.0+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env file with:
# SECRET_KEY=your-secret-key
# MONGO_URI=mongodb://localhost:27017
# DATABASE_NAME=empsphere
# JWT_SECRET=your-jwt-secret
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# CASHFREE_APP_ID=your-cashfree-app-id
# CASHFREE_SECRET_KEY=your-cashfree-secret-key
# CASHFREE_ENVIRONMENT=SANDBOX
# CASHFREE_API_VERSION=2025-01-01

python manage.py migrate
python manage.py seed_rbac  # Seed roles and super admin
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install

# Create .env file with:
# VITE_API_BASE_URL=http://localhost:8000/api
# VITE_APP_URL=http://localhost:3000

npm run dev
```

---

## 25. How to Debug

| Problem | Where to Look |
|---------|---------------|
| Login fails | Check backend logs, verify email/password, check if email verified |
| OTP doesn't arrive | Check SMTP settings in .env, check spam folder |
| Image doesn't show | Check GridFS for file, verify profile_image_id in user doc |
| Employee doesn't appear | Check filters, verify is_active status |
| Pagination doesn't work | Check page/page_size params, verify total_pages in response |
| Filter doesn't work | Check query param names match backend |
| Attendance fails | Check for duplicate records, verify employee is active |
| Payment fails | Check Cashfree credentials, verify payment status on backend |

---

## 26. Beginner Glossary

| Term | Definition |
|------|------------|
| API | Application Programming Interface - how software communicates |
| HTTP | Protocol for web communication (GET, POST, PUT, DELETE) |
| REST | Architectural style for APIs using HTTP methods |
| APIView | Django REST Framework class for handling HTTP requests |
| Serializer | Validates and transforms data between JSON and Python objects |
| DTO | Data Transfer Object - carries data between layers |
| Validator | Checks data meets business rules |
| Controller | Handles HTTP requests, delegates to services |
| Service | Contains business logic |
| Repository | Handles database operations |
| Middleware | Code that runs before/after requests |
| JWT | JSON Web Token - stateless authentication token |
| OTP | One-Time Password - temporary code for verification |
| RBAC | Role-Based Access Control - permissions based on roles |
| Redux | State management library for React |
| Hook | React function for stateful logic |
| GridFS | MongoDB file storage system for large files |
| ObjectId | MongoDB's unique identifier type |
| MongoDB Collection | Like a table in relational databases |
| Index | Database structure for faster queries |
| CRUD | Create, Read, Update, Delete operations |

---

## 27. Final Project Structure

```
EmpSphere/
├── .github/workflows/ci-backend.yml
├── .gitignore
├── .vscode/extensions.json
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── authentication/
│   │   │   ├── views/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── managers/
│   │   │   ├── serializers/
│   │   │   ├── schemas/
│   │   │   ├── dtos/
│   │   │   ├── urls.py
│   │   │   └── permissions.py
│   │   ├── employee/
│   │   ├── organization/
│   │   ├── attendance/
│   │   ├── leave/
│   │   ├── payment/
│   │   ├── activity_logs/
│   │   ├── statistics/
│   │   ├── reports/
│   │   └── common/
│   ├── templates/emails/
│   ├── .env
│   ├── requirements.txt
│   └── manage.py
├── docs/
│   ├── DEVELOPER_GUIDE.md
│   └── FINAL_AUDIT_REPORT.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── routes/
│   │   ├── config/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── package.json
```
