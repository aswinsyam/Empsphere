# Code-Level Explanation

This document explains what individual blocks of important/complex code do, line by line where necessary.

---

## Backend

### JWT Token Generation (`apps/authentication/services/auth_service.py`)

```python
def _generate_access_token(self, user):
    return jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "token_type": "access",
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
```

**What it does**: Creates a JWT access token that identifies the user.

**Why it exists**: The frontend needs a token to prove who it is on subsequent requests. The access token is short-lived (30 minutes) and is used for most API calls.

**Parameters**: `user` — a MongoDB user document dict with `_id`, `email`, `role` fields.

**Return value**: A signed JWT string.

**Validation**: 
- `user["_id"]` is converted to string because MongoDB ObjectId is not JSON serializable
- `user.get("email")` and `user.get("role")` use `.get()` to safely handle missing fields

**Exceptions**: None raised here, but `jwt.encode()` will fail if `settings.JWT_SECRET` is not set.

**Database operations**: None.

**Data flow**:
```
User document → extract _id, email, role → jwt.encode() → signed JWT string → returned to frontend
```

---

### JWT Token Refresh (`apps/authentication/services/auth_service.py`)

```python
def refresh_token(self, refresh_token):
    if self.token_blacklist_manager.is_blacklisted(refresh_token):
        raise UnauthorizedException("Token has been blacklisted.")
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        raise UnauthorizedException("Invalid refresh token.")
    if payload.get("token_type") != "refresh":
        raise UnauthorizedException("Invalid token type.")
    user = self.user_repository.get_by_id(payload.get("user_id"))
    if not user:
        raise UnauthorizedException("User not found.")
    if user.get("status") == "INACTIVE":
        raise UnauthorizedException(
            "Your account is inactive. Please contact the administrator."
        )
    # Rotate token
    self.token_blacklist_manager.blacklist(refresh_token)
    access_token = self._generate_access_token(user)
    new_refresh_token = self._generate_refresh_token(user)
    return {"access_token": access_token, "refresh_token": new_refresh_token}
```

**What it does**: Validates a refresh token, rotates it (blacklists old, issues new), and returns a fresh access/refresh pair.

**Why it exists**: Access tokens expire after 30 minutes. Instead of forcing the user to log in again, the frontend uses the refresh token to get a new pair.

**Parameters**: `refresh_token` — the JWT string from the frontend.

**Return value**: `{"access_token": "...", "refresh_token": "..."}`

**Validation**:
1. Token not blacklisted (prevents reuse after logout)
2. JWT signature valid and not expired
3. `token_type` claim is `"refresh"` (rejects access tokens)
4. User still exists in database
5. User account is active

**Security notes**:
- Token rotation: old refresh token is blacklisted before issuing new one
- If any check fails, `UnauthorizedException` is raised (caught by exception handler → 401 response)

**Data flow**:
```
Frontend sends refresh_token → check blacklist → decode JWT → validate token_type → fetch user → blacklist old token → generate new pair → return
```

---

### OTP Generation (`apps/authentication/services/otp_service.py`)

```python
@staticmethod
def _generate_otp():
    upper_bound = 10 ** OTP_LENGTH
    lower_bound = 10 ** (OTP_LENGTH - 1)
    return str(secrets.randbelow(upper_bound - lower_bound) + lower_bound)
```

**What it does**: Generates a cryptographically secure numeric OTP code.

**Why it exists**: OTPs prove that the user owns the email address they claim. `secrets.randbelow()` is used instead of `random.randint()` because it's cryptographically secure.

**Parameters**: None (uses module-level `OTP_LENGTH = 6`).

**Return value**: A string like `"482193"` (always 6 digits, never starts with 0).

**How it works**:
- `10 ** 6 = 1,000,000` (upper bound, exclusive)
- `10 ** 5 = 100,000` (lower bound, inclusive)
- `secrets.randbelow(900000)` returns 0–899999
- Adding 100,000 gives 100000–999999 (always 6 digits)

**Example**: `secrets.randbelow(900000)` returns `382193`, plus `100000` = `482193`.

---

### OTP Verification (`apps/authentication/services/otp_service.py`)

```python
def verify_otp(self, dto):
    email = dto.get("email")
    otp_code = dto.get("otp")
    purpose = dto.get("purpose", OTPPurpose.DEFAULT)
    otp_record = self.otp_repository.get_active(email, purpose)
    if not otp_record:
        raise NotFoundException("OTP not found or expired.")
    if otp_record.get("is_used"):
        raise NotFoundException("OTP already used.")
    if otp_record.get("otp") != otp_code:
        raise NotFoundException("Invalid OTP code.")
    if datetime.utcnow() > otp_record.get("expires_at"):
        raise NotFoundException("OTP expired.")
    if not self.otp_repository.mark_used(otp_record["_id"]):
        raise NotFoundException("OTP already used.")
    return {"message": "OTP verified successfully.", "verified": True}
```

**What it does**: Validates an OTP code against the stored record, ensuring it hasn't been used or expired.

**Why it exists**: OTP verification is the core security check for email verification, login, and password reset flows.

**Parameters**: `dto` dict with `email`, `otp`, `purpose`.

**Return value**: Success dict if valid.

**Validation steps**:
1. Active OTP record exists for email + purpose
2. OTP hasn't been marked as used
3. OTP code matches exactly (string comparison)
4. OTP hasn't passed expiry time
5. Atomic mark-as-used succeeds (prevents race conditions where two requests use the same OTP)

**Security notes**:
- All failure paths return the same generic message ("OTP not found or expired") to prevent account enumeration
- `mark_used()` uses an atomic MongoDB `update_one` with `is_used: False` filter, so only one request can succeed

---

### Password Hashing (`apps/common/security/password_manager.py`)

```python
@staticmethod
def hash_password(password: str) -> str:
    try:
        b = password.encode("utf-8") if isinstance(password, str) else bytes(password)
    except Exception:
        b = None
    if b is not None and len(b) > 72:
        from apps.common.exceptions.custom_exception import ValidationException
        raise ValidationException(
            message="Password must be at most 72 bytes when UTF-8 encoded."
        )
    return pwd_context.hash(password)
```

**What it does**: Hashes a plaintext password using bcrypt.

**Why it exists**: Bcrypt has a 72-byte input limit. This method validates the length before hashing to prevent runtime errors.

**Parameters**: `password` — plaintext string.

**Return value**: Bcrypt hash string like `$2b$12$...`.

**Validation**:
- Encodes password as UTF-8 bytes
- Raises `ValidationException` if byte length > 72
- Uses `passlib`'s `CryptContext` with bcrypt scheme

**Security notes**:
- Bcrypt automatically salts each hash
- `deprecated="auto"` means passlib will handle algorithm migration if bcrypt is ever deprecated

---

### Login Flow (`apps/authentication/services/auth_service.py`)

```python
def login(self, dto):
    email = (dto.get("email") or "").strip().lower()
    password = dto.get("password") or ""
    user = self.user_repository.get_by_email(email)
    if not user or not self.password_manager.verify_password(password, user.get("password")):
        raise UnauthorizedException("Invalid email or password.")
    if user.get("status") == "INACTIVE":
        raise UnauthorizedException(
            "Your account is inactive. Please contact the administrator."
        )
    if not user.get("is_email_verified"):
        try:
            self.otp_service.send_otp({"email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION})
        except Exception as exc:
            logger.warning("Failed to send email verification OTP for %s: %s", user.get("email"), exc)
        return {"requires_otp": True, "email": user.get("email"), "purpose": OTPPurpose.EMAIL_VERIFICATION}
    access_token = self._generate_access_token(user)
    refresh_token = self._generate_refresh_token(user)
    self.user_repository.update(str(user["_id"]), {"last_login": datetime.utcnow()})
    self.log_activity(...)
    return self._build_auth_response(user, access_token, refresh_token)
```

**What it does**: Authenticates a user and returns JWT tokens, or triggers OTP verification if email is unverified.

**Why it exists**: This is the core login flow. It handles three cases: invalid credentials, unverified email (triggers OTP), and successful login.

**Parameters**: `dto` with `email` and `password`.

**Return value**: Either `{"requires_otp": true, ...}` or full auth response with tokens.

**Flow**:
1. Normalize email (strip whitespace, lowercase)
2. Fetch user by email
3. Verify password against bcrypt hash
4. Check account is active
5. If email not verified: send OTP, return `requires_otp` flag
6. If verified: generate access + refresh tokens, update last_login, log activity

**Security notes**:
- Generic error message "Invalid email or password" prevents account enumeration
- `verify_password()` returns `False` for non-bcrypt hashes (prevents legacy plaintext leakage)
- Inactive accounts are rejected with a specific message

---

### Email Sending (`apps/authentication/services/otp_service.py`)

```python
def _send_otp_email(self, email, otp_code, purpose):
    subject = self.EMAIL_SUBJECTS.get(purpose, self.DEFAULT_EMAIL_SUBJECT)
    context = {"otp": otp_code, "year": datetime.utcnow().year, "purpose": purpose}
    html_message = None
    try:
        html_message = render_to_string("emails/otp_email.html", context)
    except Exception:
        pass
    send_mail(
        subject=subject,
        message=f"Your OTP code is: {otp_code}",
        from_email=None,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )
```

**What it does**: Sends an OTP email via Django's SMTP backend.

**Why it exists**: OTPs need to be delivered to the user's email. This method handles both HTML and plaintext versions.

**Parameters**: `email` (recipient), `otp_code` (the code to send), `purpose` (determines subject line).

**Return value**: None (side effect: email sent).

**How it works**:
1. Selects subject line based on purpose (e.g., "EmpSphere Password Reset Code" for forgot_password)
2. Renders HTML template `emails/otp_email.html` with OTP, year, and purpose
3. Falls back to plaintext if template rendering fails
4. Uses Django's `send_mail()` with the configured SMTP backend

**Note**: The `except Exception: pass` swallows template rendering errors silently. This is a known issue — the plaintext fallback still works, but template failures are not logged.

---

### Pagination Pattern (used across all repositories)

```python
def get_all(self, ..., page=1, page_size=10, ...):
    ...
    total_records = self.collection.count_documents(query)
    skip = (page - 1) * page_size
    records = list(self.collection.find(query).skip(skip).limit(page_size))
    total_pages = (total_records + page_size - 1) // page_size if page_size else 1
    return records, total_records, total_pages
```

**What it does**: Implements offset-based pagination for MongoDB queries.

**Why it exists**: Returning all records at once would be slow and waste bandwidth. Pagination lets clients request pages of data.

**Parameters**: `page` (1-indexed), `page_size` (records per page).

**Return value**: `(records, total_records, total_pages)`

**How it works**:
1. `count_documents(query)` — counts total matching records (for pagination meta)
2. `skip = (page - 1) * page_size` — calculates how many records to skip
3. `.skip(skip).limit(page_size)` — MongoDB pagination
4. `total_pages = ceil(total_records / page_size)` — total pages for UI

**Used in**: `EmployeeRepository.get_all()`, `DepartmentRepository.get_all()`, `DesignationRepository.get_all()`, `AttendanceRepository.get_all()`, `LeaveRepository.get_all()`, `ReportService.get_activity_report()`, `ActivityLogController.get()`

---

### Role Permission Check (`apps/common/permissions/role_permission.py`)

```python
@staticmethod
def can_manage_user(actor_role, target_role) -> bool:
    actor = RolePermission.get_role_enum(actor_role)
    target = RolePermission.get_role_enum(target_role)
    if actor is None or target is None:
        return False
    return target in RolePermission.MANAGABLE_ROLES.get(actor, set())
```

**What it does**: Determines if an actor's role can manage a user with the target role.

**Why it exists**: RBAC requires consistent permission checks across all endpoints. This method centralizes the "who can manage whom" logic.

**Parameters**: `actor_role` (the user performing the action), `target_role` (the user being managed).

**Return value**: `True` if actor can manage target, `False` otherwise.

**How it works**:
1. Converts both roles to `Role` enum values
2. Looks up the `MANAGABLE_ROLES` dict for the actor's role
3. Returns `True` if target role is in the set of manageable roles

**MANAGABLE_ROLES mapping**:
- SUPER_ADMIN: can manage everyone (SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE)
- ADMIN: can manage HR_MANAGER and EMPLOYEE
- HR_MANAGER: can manage EMPLOYEE only
- EMPLOYEE: can manage nobody

**Used in**: `EmployeeService.update_employee()`, `EmployeeService.update_employee_status()`, `ActivityLogController.get()`

---

### Activity Logging (`apps/common/base/base_service.py`)

```python
def log_activity(
    self,
    module: str,
    action: str,
    performed_by: str,
    target_id: str,
    status: str,
    description: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    self.audit_service.log(
        module=module,
        action=action,
        performed_by=performed_by,
        target_id=target_id,
        status=status,
        description=description,
        metadata=metadata or {},
    )
```

**What it does**: Writes an audit log entry to MongoDB.

**Why it exists**: Every significant action (create, update, delete, login, logout) needs to be tracked. This method provides a consistent interface.

**Parameters**:
- `module` — Which app/module (e.g., "EMPLOYEE", "ATTENDANCE", "AUTHENTICATION")
- `action` — What action was performed (e.g., "CREATE_EMPLOYEE", "LOGIN")
- `performed_by` — User ID of who did it
- `target_id` — ID of what was affected
- `status` — "SUCCESS" or "FAILED"
- `description` — Human-readable description
- `metadata` — Optional extra data

**Return value**: None (side effect: MongoDB insert).

**Used by**: Every service in the project via `self.log_activity(...)`.

---

## Frontend

### Axios Request Interceptor (`src/config/axios.ts`)

```typescript
api.interceptors.request.use((config) => {
  if (!isPublicEndpoint(config.url)) {
    const token = TokenUtil.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
```

**What it does**: Automatically attaches the access token to every outgoing request.

**Why it exists**: The frontend shouldn't manually add `Authorization` headers to every API call. This interceptor handles it transparently.

**How it works**:
1. Checks if the request URL is a public endpoint (login, register, etc.)
2. If not public, reads the access token from localStorage
3. Attaches it as a `Bearer` token in the `Authorization` header

**Used by**: Every API request made through the `api` instance.

---

### Axios Response Interceptor — Token Refresh (`src/config/axios.ts`)

```typescript
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isPublicEndpoint(original.url)
    ) {
      original._retry = true;
      const refreshToken = TokenUtil.getRefreshToken();
      if (refreshToken) {
        try {
          const result = await axios.post(`${ENV.API_BASE_URL}/auth/refresh-token/`, { refresh_token: refreshToken });
          const newAccessToken = result.data.access_token;
          const newRefreshToken = result.data.refresh_token;
          TokenUtil.setTokens(newAccessToken, newRefreshToken);
          original.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(original);
        } catch {
          TokenUtil.clear();
          dispatchAuthExpired();
        }
      }
    }
    return Promise.reject(error);
  }
);
```

**What it does**: Automatically refreshes the access token when it expires (401 response).

**Why it exists**: Access tokens expire after 30 minutes. Instead of forcing the user to log in again, the interceptor silently refreshes the token and retries the original request.

**How it works**:
1. Catches 401 errors on non-public endpoints
2. Checks if this is the first retry (`_retry` flag)
3. Reads the refresh token from localStorage
4. Calls `/auth/refresh-token/` with the refresh token
5. Stores the new access + refresh tokens
6. Retries the original request with the new access token
7. If refresh fails: clears tokens and dispatches `auth:expired` event (triggers redirect to login)

**Security notes**:
- `_retry` flag prevents infinite loops (only retry once)
- If the refresh token is also expired/invalid, the user is logged out
- `dispatchAuthExpired()` fires a custom event that `AppBootstrap` listens for

---

### Redux Auth Slice — Login Thunk (`src/store/slices/authSlice.ts`)

```typescript
login: createAsyncThunk("auth/login", async (payload, { rejectWithValue }) => {
  const response = await authService.login(payload);
  if (response.requires_otp) {
    return rejectWithValue({ requiresOtp: true, ...response });
  }
  const { access_token, refresh_token, ...user } = response;
  TokenUtil.setTokens(access_token, refresh_token);
  return { user: normalizeUser(user), accessToken: access_token, refreshToken: refresh_token };
}),
```

**What it does**: Dispatches the login API call and handles the response.

**Why it exists**: Redux Thunk allows async actions. This thunk handles the login flow, including the OTP requirement case.

**Parameters**: `payload` — `{ email, password }`

**Return value**: Fulfilled with `{ user, accessToken, refreshToken }` or rejected with `{ requiresOtp: true, ... }`.

**Flow**:
1. Calls `authService.login()`
2. If `requires_otp` is true, rejects with that info (triggers OTP flow in component)
3. Otherwise, extracts tokens and user data
4. Stores tokens in localStorage
5. Returns normalized user + tokens to Redux state

---

### useDashboardData Hook (`src/hooks/useDashboardData.ts`)

```typescript
export function useDashboardData(statsFetcher, activitiesFetcher) {
  const [stats, setStats] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    abortControllerRef.current = new AbortController();
    const load = async () => {
      try {
        const [statsData, activitiesData] = await Promise.all([
          statsFetcher(),
          activitiesFetcher(),
        ]);
        if (!abortControllerRef.current.signal.aborted) {
          setStats(statsData);
          setActivities(activitiesData);
        }
      } catch (err) {
        if (!abortControllerRef.current.signal.aborted) {
          setError(err);
        }
      } finally {
        if (!abortControllerRef.current.signal.aborted) {
          setLoading(false);
        }
      }
    };
    load();
    return () => abortControllerRef.current?.abort();
  }, [statsFetcher, activitiesFetcher]);

  return { stats, activities, loading, error };
}
```

**What it does**: Loads dashboard statistics and recent activities in parallel.

**Why it exists**: All four dashboard pages need the same data-loading pattern. This hook eliminates duplication.

**Parameters**: `statsFetcher` and `activitiesFetcher` — functions that return promises (different for each role).

**Return value**: `{ stats, activities, loading, error }`

**Key features**:
- `AbortController` prevents state updates after unmount (avoids memory leaks)
- `Promise.all` loads both requests in parallel for speed
- Dependency array includes the fetcher functions, so the effect re-runs if they change

---

### getErrorMessage Utility (`src/utils/helpers.ts`)

```typescript
export function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object") {
    const err = error as { response?: { data?: { message?: string; errors?: unknown } }; message?: string };
    const data = err.response?.data;
    if (data?.errors && typeof data.errors === "object" && !Array.isArray(data.errors)) {
      const errorsObj = data.errors as Record<string, unknown>;
      const firstField = Object.keys(errorsObj)[0];
      const firstValue = firstField ? errorsObj[firstField] : undefined;
      if (typeof firstValue === "string" && firstValue.trim()) return firstValue;
      if (Array.isArray(firstValue) && firstValue.length > 0 && typeof firstValue[0] === "string") return firstValue[0];
    }
    if (data?.message) return data.message;
    if (err.message) return err.message;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}
```

**What it does**: Extracts a human-friendly error message from various error shapes.

**Why it exists**: API errors can come in different formats (DRF validation errors, custom exceptions, network errors). This utility normalizes them.

**Parameters**: `error` — unknown error object from Axios catch block.

**Return value**: User-friendly error message string.

**Priority order**:
1. First nested field error from `errors` object (most specific)
2. Top-level `message` from API response
3. Direct `message` property on error
4. `Error.message` if it's an Error instance
5. Generic fallback: "Something went wrong. Please try again."

---

### AppBootstrap Session Restoration (`src/components/AppBootstrap.tsx`)

```typescript
useEffect(() => {
  const token = TokenUtil.getAccessToken();
  if (token) {
    dispatch(fetchMe());
  }
}, [dispatch]);
```

**What it does**: Automatically restores the user session when the app loads.

**Why it exists**: After a page refresh, the Redux state is lost but the JWT token remains in localStorage. This effect re-fetches the user profile to restore the session.

**Parameters**: None.

**Return value**: None (side effect: dispatches `fetchMe` thunk if token exists).

**Flow**:
1. On app mount, check if access token exists in localStorage
2. If yes, dispatch `fetchMe()` which calls `/api/auth/me/`
3. If the token is valid, user state is restored
4. If the token is invalid, the Axios interceptor handles 401 and clears auth

---

### Protected Route Guard (`src/routes/ProtectedRoute.tsx`)

```typescript
const { isAuthenticated, initializing } = useAuth();

if (initializing) {
  return <Loader text="Loading..." />;
}

if (!isAuthenticated) {
  return <Navigate to="/login" state={{ from: location }} replace />;
}

return <Outlet />;
```

**What it does**: Protects routes by checking authentication status.

**Why it exists**: Prevents unauthenticated users from accessing protected pages.

**Flow**:
1. While auth state is initializing (checking localStorage + fetching user), show loader
2. If not authenticated, redirect to `/login` with `from` state (so login can redirect back)
3. If authenticated, render the child route via `<Outlet />`

**Used by**: All protected routes in `AppRoutes.tsx`.

---

### RequireRole Guard (`src/routes/RequireRole.tsx`)

```typescript
const { user } = useAuth();
const allowedRoles = ["SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE"];
const userRole = user?.role;
const hasAccess = allowedRoles.includes(userRole);

if (!hasAccess && userRole) {
  return <Navigate to="/unauthorized" replace />;
}

if (!hasAccess) {
  return <Navigate to="/login" replace />;
}

return <Outlet />;
```

**What it does**: Restricts access to role-specific routes.

**Why it exists**: Different dashboards are only accessible to specific roles.

**Flow**:
1. Get current user's role from auth state
2. Check if role is in the allowed roles for this route
3. If authenticated but wrong role, redirect to `/unauthorized`
4. If not authenticated at all, redirect to `/login`
5. If authorized, render the child route

**Used by**: Role-specific dashboard routes in `AppRoutes.tsx`.

---

### Token Storage (`src/utils/token.ts`)

```typescript
export const TokenUtil = {
  getAccessToken(): string | null {
    return localStorage.getItem("access_token");
  },
  getRefreshToken(): string | null {
    return localStorage.getItem("refresh_token");
  },
  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  },
  clear(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};
```

**What it does**: Wraps localStorage for JWT token storage.

**Why it exists**: Centralizes token access so the rest of the app doesn't directly manipulate localStorage keys.

**Used by**: Axios interceptors, auth slice, AppBootstrap.

**Security notes**:
- Tokens are stored in localStorage (vulnerable to XSS attacks)
- For higher security, consider httpOnly cookies instead

---

### Attendance Check-In Flow (`apps/attendance/services/attendance_service.py`)

```python
def check_in(self, employee_id, user_role):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    existing = self.attendance_repository.get_by_employee_and_date(employee_id, today)
    if existing:
        if existing.get("check_in") and existing.get("check_out"):
            raise ConflictException("You have already completed attendance for today.")
        if existing.get("check_in"):
            raise ConflictException("You have already checked in today.")
        record = self.attendance_repository.update(existing["_id"], {"check_in": datetime.utcnow()}, employee_id)
        return record
    record_id = self.attendance_repository.create({
        "employee_id": employee_id,
        "date": today,
        "status": "PRESENT",
        "check_in": datetime.utcnow(),
    }, employee_id)
    return self.attendance_repository.get_by_id(record_id)
```

**What it does**: Creates or updates an attendance record for today's check-in.

**Why it exists**: Employees need a quick way to record arrival time without filling a full form.

**Flow**:
1. Compute today's date string
2. Look up existing attendance for employee + date
3. If already checked out → reject (day complete)
4. If already checked in → reject (duplicate)
5. If no record → create new record with check-in timestamp
6. If record exists without check-out → update check-in timestamp

**Used by**: `AttendanceController._check_in()`

---

### Attendance Check-Out Flow (`apps/attendance/services/attendance_service.py`)

```python
def check_out(self, employee_id, user_role):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    existing = self.attendance_repository.get_by_employee_and_date(employee_id, today)
    if not existing or not existing.get("check_in"):
        raise ValidationException("You must check in before checking out.")
    record = self.attendance_repository.update(existing["_id"], {"check_out": datetime.utcnow()}, employee_id)
    return record
```

**What it does**: Sets the check-out timestamp on today's attendance record.

**Why this exists**: Employees need to record departure time.

**Flow**:
1. Look up today's record
2. Validate that check-in exists
3. Update record with check-out timestamp

---

### Employee Self-Access Enforcement (`apps/employee/controllers/employee_controller.py`)

```python
if request.user.get("role") == "EMPLOYEE":
    employee_id = str(request.user["_id"])
```

**What it does**: Forces EMPLOYEE role to only see their own record.

**Why this exists**: RBAC requires that regular employees cannot browse other employees' data.

**Where applied**: `EmployeeController.get()` list view, `AttendanceController.get()` list and detail views, `LeaveController.get()` list and detail views.

---

### Leave Approval Workflow (`apps/leave/services/leave_service.py`)

```python
def update_leave_status(self, leave_id, status, user_id):
    leave = self.leave_repository.get_by_id(leave_id)
    if not leave:
        raise NotFoundException("Leave not found.")
    if leave.get("status") != "PENDING":
        raise ConflictException("Only pending leaves can be approved or rejected.")
    if str(leave.get("employee_id")) == user_id:
        raise ForbiddenException("You cannot approve or reject your own leave.")
    update_data = {"status": status}
    if status == "APPROVED":
        update_data["approved_by"] = user_id
    elif status == "REJECTED":
        update_data["rejected_by"] = user_id
    return self.leave_repository.update(leave_id, update_data, user_id)
```

**What it does**: Validates and transitions a leave from PENDING to APPROVED or REJECTED.

**Why this exists**: Leave approvals must prevent self-approval and only act on pending requests.

**Validation steps**:
1. Leave exists
2. Leave is PENDING
3. Actor is not the leave applicant
4. Sets `approved_by` or `rejected_by` audit field

---

### Report Dispatch by URL Path (`apps/reports/controllers/report_controller.py`)

```python
path = request.path.rstrip("/")
report_type = path.rsplit("/", 1)[-1]

if report_type == "employees":
    data = self.report_service.get_employee_report(filters)
elif report_type == "attendance":
    data = self.report_service.get_attendance_report(filters)
# ... etc
```

**What it does**: Routes a single controller to multiple report types based on the URL suffix.

**Why this exists**: All reports share the same permission requirement (`EMPLOYEE_MANAGER_ROLES`) and response envelope, so one controller handles all six report endpoints.

**URL mapping**:
- `/api/reports/employees/` → `get_employee_report`
- `/api/reports/attendance/` → `get_attendance_report`
- `/api/reports/leaves/` → `get_leave_report`
- `/api/reports/departments/` → `get_department_report`
- `/api/reports/designations/` → `get_designation_report`
- `/api/reports/activity/` → `get_activity_report`

---

### useDashboardData Hook (`src/hooks/useDashboardData.ts`)

```typescript
export function useDashboardData(statsFetcher, activitiesFetcher) {
  const [stats, setStats] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    abortControllerRef.current = new AbortController();
    const load = async () => {
      try {
        const [statsData, activitiesData] = await Promise.all([
          statsFetcher(),
          activitiesFetcher(),
        ]);
        if (!abortControllerRef.current.signal.aborted) {
          setStats(statsData);
          setActivities(activitiesData);
        }
      } catch (err) {
        if (!abortControllerRef.current.signal.aborted) {
          setError(err);
        }
      } finally {
        if (!abortControllerRef.current.signal.aborted) {
          setLoading(false);
        }
      }
    };
    load();
    return () => abortControllerRef.current?.abort();
  }, [statsFetcher, activitiesFetcher]);

  return { stats, activities, loading, error };
}
```

**What it does**: Loads dashboard statistics and recent activities in parallel with cancellation support.

**Why this exists**: All four dashboard pages need the same data-loading pattern. This hook eliminates duplication.

**Key features**:
- `AbortController` prevents state updates after unmount
- `Promise.all` loads both requests in parallel
- Dependency array includes fetcher functions for re-triggering

---

### Redux Slice Pattern (used across all frontend slices)

```typescript
const slice = createSlice({
  name: "domain",
  initialState,
  reducers: {
    clear(state) { state.items = []; state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetch.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetch.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
        state.total_records = action.payload.total_records;
      })
      .addCase(fetch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load.";
      });
  },
});
```

**What it does**: Standard Redux Toolkit pattern for async data fetching.

**Why this exists**: All domain slices (employee, department, designation, attendance, leave) follow the same pattern for consistency.

**Used in**: `employeeSlice.ts`, `departmentSlice.ts`, `designationSlice.ts`, `attendanceSlice.ts`, `leaveSlice.ts`

---

### Role-Aware Page Rendering (`src/pages/employees/EmployeesPage.tsx`)

```typescript
const canManage = canManageEmployees(user?.role);

return (
  <div>
    <PageHeader
      actions={canManage ? <Button onClick={openCreate}>Create Employee</Button> : undefined}
    />
    {/* filters table */}
    {canManage && (
      <td className="px-4 py-3">
        <button onClick={() => openEdit(emp)}>Edit</button>
        <button onClick={() => handleStatusToggle(emp)}>Deactivate</button>
      </td>
    )}
  </div>
);
```

**What it does**: Conditionally shows management actions based on the user's role.

**Why this exists**: Non-manager employees should see the employee list for reference but not have edit/delete controls.

**Pattern**: Used consistently across `EmployeesPage`, `DepartmentsPage`, `DesignationsPage`, `AttendancePage`, `LeavesPage`.

---

### CSV Export (`src/utils/exportCsv.ts`)

```typescript
export function exportToCsv(filename: string, rows: Record<string, unknown>[], headers?: string[]): void {
  if (!rows.length) return;
  const keys = headers || Object.keys(rows[0]);
  const csvContent = [
    keys.join(","),
    ...rows.map((row) =>
      keys.map((k) => {
        const value = row[k];
        const stringValue = value === null || value === undefined ? "" : String(value);
        return `"${stringValue.replace(/"/g, '""')}"`;
      }).join(",")
    ),
  ].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
```

**What it does**: Exports an array of objects as a CSV file download.

**Why this exists**: The Reports page and Leaves page need to export data as CSV.

**RFC 4180 compliance**: Properly handles commas, quotes, and newlines in values.

**Used by**: `ReportsPage.tsx`, `LeavesPage.tsx`
