/**
 * ToastProvider.
 *
 * Centralized toast notification provider built on `react-toastify`.
 * Should be mounted at the application root (e.g. `App.tsx`). Exposes
 * helper functions (`toastSuccess`, `toastError`) and
 * centralized constants (`AuthToasts`) for consistent UX across auth
 * and business flows.
 */

import React from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

/**
 * ToastProvider component.
 * Renders the ToastContainer alongside the children.
 */
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      <ToastContainer
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick={true}
        aria-label="Notifications"
      />
      {children}
    </>
  );
};

/**
 * Toast messages for authentication flows.
 * Use these in components for consistent UX.
 */
export const AuthToasts = {
  registrationSuccess: "Registration initiated. Please check your email to verify your account.",
  emailAlreadyExists: "Email already exists.",
  invalidCredentials: "Invalid email or password.",
  otpSent: "OTP sent to your email.",
  otpVerified: "Email verified successfully.",
  otpVerifiedSuccess: "OTP verified successfully.",
  passwordChanged: "Password changed successfully.",
  passwordResetSuccess: "Password reset successful.",
  googleLoginSuccess: "Google login successful.",
  logoutSuccess: "Logged out successfully.",
  profileUpdated: "Profile updated successfully.",
  profileImageUploaded: "Profile image uploaded successfully.",
  apiError: "An error occurred. Please try again.",
  validationError: "Validation failed. Please check your inputs.",
};

/**
 * Simple toast functions.
 */
export const toastSuccess = (message: string) => toast.success(message);
export const toastError = (message: string) => toast.error(message);

const showApiError = (error: any): string => {
  if (!error) return AuthToasts.apiError;

  if (error.response) {
    const data = error.response.data;
    if (typeof data === "string") return data;
    if (data && typeof data === "object") {
      if (data.message) return String(data.message);
      if (data.detail) return String(data.detail);
      if (data.error) return String(data.error);
      if (data.non_field_errors) return String(data.non_field_errors);
      if (data.errors) {
        const errMessages: string[] = [];
        Object.values(data.errors).forEach((err: any) => {
          if (err && err.message) errMessages.push(String(err.message));
        });
        return errMessages.length > 0 ? errMessages.join(", ") : AuthToasts.apiError;
      }
    }
  }

  if (error.message) return String(error.message);
  if (error.error) return String(error.error);
  if (error.detail) return String(error.detail);

  return AuthToasts.apiError;
};

/**
 * Show a toast with an API error.
 */
export const toastApiError = (error: any, prefix?: string) => {
  const message = showApiError(error);
  toast.error(prefix ? `${prefix}: ${message}` : message);
};
