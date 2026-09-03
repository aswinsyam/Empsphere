/**
 * Auth API service.
 * Calls the backend authentication endpoints.
 */

import { http } from "./api";
import {
  ForgotPasswordPayload,
  LoginPayload,
  LoginResult,
  RegisterResult,
  ResetPasswordPayload,
  SendOTPPayload,
  SetPasswordPayload,
  VerifyOTPPayload,
} from "@/types/auth";

/** Client for authentication-related API endpoints. */
export const authService = {
  /** Log in and get tokens. */
  async login(payload: LoginPayload): Promise<LoginResult> {
    return http.post<LoginResult>("/auth/login/", payload);
  },

  /** Register a new admin account (requires company secret). */
  async register(payload: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    confirm_password: string;
    company_secret: string;
    phone?: string;
  }): Promise<RegisterResult> {
    return http.post<RegisterResult>("/auth/register/", payload);
  },

  /** Log in with a Google ID token. */
  async googleLogin(idToken: string): Promise<LoginResult> {
    return http.post<LoginResult>("/auth/google-login/", {
      id_token: idToken,
    });
  },

/** Log out (blacklist tokens). */
  async logout(refreshToken: string): Promise<void> {
    await http.post<null>("/auth/logout/", { refresh_token: refreshToken });
  },

  /** Send an OTP to an email for verification or password setup. */
  async sendOtp(payload: SendOTPPayload): Promise<null> {
    return http.post<null>("/auth/send-otp/", payload);
  },

  /** Verify an OTP code. */
  async verifyOtp(payload: VerifyOTPPayload): Promise<any> {
    return http.post<any>("/auth/verify-otp/", payload);
  },

  /** Set a local password for a Google-authenticated user (requires OTP). */
  async setPassword(payload: SetPasswordPayload): Promise<null> {
    return http.post<null>("/auth/set-password/", payload);
  },

  /** Request a password reset OTP (`purpose: "forgot_password"`). */
  async forgotPassword(payload: ForgotPasswordPayload): Promise<null> {
    return http.post<null>("/auth/forgot-password/", payload);
  },

  /**
   * Reset the password using the single-use reset token returned by
   * `verifyOtp({ purpose: "forgot_password" })`.
   */
  async resetPassword(payload: ResetPasswordPayload): Promise<null> {
    return http.post<null>("/auth/reset-password/", payload);
  },
};
