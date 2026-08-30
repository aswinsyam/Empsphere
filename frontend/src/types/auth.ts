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
  profile_image_id?: string;
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
  employee_code?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email: string;
  phone?: string;
  role?: string;
  profile_image_id?: string;
  is_email_verified?: boolean;
  login_provider?: string;
  access_token?: string;
  refresh_token?: string;
  requires_otp?: boolean;
  purpose?: string;
}

/** Payload returned after a successful registration. */
export interface RegisterResult {
  user_id: string;
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

/** Login request body. */
export interface LoginPayload {
  email: string;
  password: string;
}

/** Set password request body (Google users). */
export interface SetPasswordPayload {
  otp: string;
  new_password: string;
}

/** Forgot password request body. */
export interface ForgotPasswordPayload {
  email: string;
}

/**
 * Reset password request body.
 *
 * The reset is authorized by the single-use `reset_token` returned by
 * `verify-otp` with `purpose: "forgot_password"`.
 */
export interface ResetPasswordPayload {
  reset_token: string;
  password: string;
  confirm_password: string;
}

/** Send OTP request body. */
export interface SendOTPPayload {
  email?: string;
  purpose?: string;
}

/** Verify OTP request body. */
export interface VerifyOTPPayload {
  email: string;
  otp: string;
  purpose?: string;
}
