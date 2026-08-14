/**
 * Authentication-related types.
 */

/** The user object returned by the backend. */
export interface User {
  _id: string;
  employee_code?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email: string;
  phone?: string;
  role: string;
  profile_image?: string;
  is_email_verified?: boolean;
  is_active?: boolean;
  last_login?: string | null;
  login_provider?: string;
}

/**
 * Payload returned after a login attempt.
 *
 * When the user's email is not yet verified, the backend responds with
 * `requires_otp: true` and no tokens. Otherwise, the full token payload
 * is returned.
 */
export interface LoginResult {
  user_id?: string;
  email: string;
  role?: string;
  access_token?: string;
  refresh_token?: string;
  requires_otp?: boolean;
}

/** Payload returned after a successful registration. */
export interface RegisterResult {
  user_id: string;
}

/** Decoded JWT payload. */
export interface DecodedToken {
  user_id: string;
  email: string;
  role: string;
  token_type: "access" | "refresh";
  exp: number;
  iat: number;
}

/** Login request body. */
export interface LoginPayload {
  email: string;
  password: string;
}

/** Register request body. */
export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
  company_secret: string;
  phone?: string;
}

/** Refresh token request body. */
export interface RefreshTokenPayload {
  refresh_token: string;
}

/** Change password request body. */
export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

/** Forgot password request body. */
export interface ForgotPasswordPayload {
  email: string;
}

/** Reset password request body. */
export interface ResetPasswordPayload {
  token: string;
  new_password: string;
}

/** Set password request body (Google users). */
export interface SetPasswordPayload {
  otp: string;
  new_password: string;
}

/** Create user request body (Admin/HR/Employee). */
export interface CreateUserPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  phone?: string;
  role: string;
  department_id?: string | null;
  designation_id?: string | null;
}

/** Send OTP request body. */
export interface SendOTPPayload {
  email?: string;
  purpose?: "email_verification" | "password_reset" | "password_setup";
}

/** Verify OTP request body. */
export interface VerifyOTPPayload {
  email: string;
  otp: string;
  purpose?: "email_verification" | "password_reset" | "password_setup";
}
