/**
 * Auth API service.
 * Calls the backend authentication endpoints.
 */

import { http } from "./api";
import {
  LoginOTPResult,
  LoginPayload,
  LoginResult,
  RegisterResult,
  SendOTPPayload,
  SetPasswordPayload,
  VerifyOTPPayload,
} from "@/types/auth";

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

  /** Login with OTP (passwordless). */
  async loginWithOtp(email: string, otp: string): Promise<LoginOTPResult> {
    return http.post<LoginOTPResult>("/auth/verify-otp/", {
      email,
      otp,
      purpose: "login",
    });
  },

/** Refresh the access token (backend rotates and returns a new refresh token). */
  async refreshToken(
    refreshToken: string
  ): Promise<{ access_token: string; refresh_token: string }> {
    return http.post<{ access_token: string; refresh_token: string }>(
      "/auth/refresh-token/",
      { refresh_token: refreshToken }
    );
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

  /** Request a password reset link. */
  async forgotPassword(email: string): Promise<null> {
    return http.post<null>("/auth/forgot-password/", { email });
  },

/** Reset the password with a token. */
  async resetPassword(token: string, newPassword: string): Promise<null> {
    return http.post<null>("/auth/reset-password/", {
      token,
      new_password: newPassword,
    });
  },

  /** Send an OTP to an email for verification or password reset. */
  async sendOtp(payload: SendOTPPayload): Promise<null> {
    return http.post<null>("/auth/send-otp/", payload);
  },

  /** Verify an OTP code. */
  async verifyOtp(payload: VerifyOTPPayload): Promise<null | LoginOTPResult> {
    return http.post<null | LoginOTPResult>("/auth/verify-otp/", payload);
  },

  /** Set a local password for a Google-authenticated user (requires OTP). */
  async setPassword(payload: SetPasswordPayload): Promise<null> {
    return http.post<null>("/auth/set-password/", payload);
  },
};
