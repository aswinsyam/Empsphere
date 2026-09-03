/**
 * ResetPasswordForm.
 *
 * Steps 2 and 3 of the forgot-password flow:
 *
 *   1. Verify the `forgot_password` OTP. A successful verification does
 *      NOT log the user in; the backend returns a short-lived, single-use
 *      `reset_token` that only authorizes a password reset.
 *   2. Set and confirm the new password, which is submitted together with
 *      the reset token.
 *
 * On success the user is redirected to the login page.
 */

import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage, getPasswordRequirements } from "@/utils/helpers";
import { ROUTES } from "@/utils/constants";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

const RESEND_COOLDOWN_SECONDS = 30;

interface ResetPasswordFormProps {
  email?: string;
}

export function ResetPasswordForm({ email = "" }: ResetPasswordFormProps) {
  const navigate = useNavigate();

  const [emailValue, setEmailValue] = useState(email);
  const [otp, setOtp] = useState("");
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [verifying, setVerifying] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const passwordRequirements = getPasswordRequirements(newPassword);
  const isPasswordValid = passwordRequirements.every((req) => req.met);
  const confirmTouched = confirmPassword.length > 0;
  const passwordsMatch = newPassword === confirmPassword;

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  /** Step 2: verify the OTP and keep the returned reset token. */
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setVerifying(true);
    try {
      const result = await authService.verifyOtp({
        email: emailValue,
        otp,
        purpose: "forgot_password",
      });
      if (!result?.reset_token) {
        throw new Error("OTP verification did not return a reset token.");
      }
      setResetToken(result.reset_token);
      setSuccess("OTP verified. Please set your new password.");
      toastSuccess(AuthToasts.otpVerifiedSuccess);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setVerifying(false);
    }
  };

  /** Request a fresh OTP; any previously sent OTP stops working. */
  const handleResendOtp = useCallback(async () => {
    if (resendCooldown > 0 || resending) return;
    setError(null);
    setSuccess(null);
    setResending(true);
    try {
      await authService.forgotPassword({ email: emailValue });
      setSuccess("A new OTP has been sent to your email.");
      toastSuccess(AuthToasts.otpSent);
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setResending(false);
    }
  }, [emailValue, resendCooldown, resending]);

  /** Step 3: set the new password using the reset token. */
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!resetToken) {
      setError("Please verify the OTP sent to your email first.");
      return;
    }

    if (!isPasswordValid) {
      const msg = "Please meet all password requirements before continuing.";
      setError(msg);
      toastError(msg);
      return;
    }

    if (!passwordsMatch) {
      const msg = "New password and confirm password do not match.";
      setError(msg);
      toastError(msg);
      return;
    }

    setSubmitting(true);
    try {
      await authService.resetPassword({
        reset_token: resetToken,
        password: newPassword,
        confirm_password: confirmPassword,
      });
      setSuccess("Password reset successful. Redirecting you to login...");
      toastSuccess(AuthToasts.passwordResetSuccess);
      setTimeout(() => navigate(ROUTES.LOGIN, { replace: true }), 1800);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}
      {success ? (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>
      ) : null}

      {!resetToken ? (
        /* ---------------- Step 2: OTP verification ---------------- */
        <form onSubmit={handleVerifyOtp} className="space-y-4">
          <Input
            label="Email"
            name="email"
            type="email"
            value={emailValue}
            onChange={(e) => setEmailValue(e.target.value)}
            placeholder="you@company.com"
            autoComplete="email"
            required
          />
          <Input
            label="OTP Code"
            name="otp"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit code"
            inputMode="numeric"
            maxLength={6}
            autoComplete="one-time-password"
            hint="The code sent to your email is valid for 10 minutes and can be used once."
            required
          />
          <Button type="submit" className="w-full" loading={verifying}>
            Verify OTP
          </Button>
          <div className="text-center">
            <Button
              type="button"
              variant="ghost"
              className="text-sm"
              loading={resending}
              disabled={resendCooldown > 0}
              onClick={handleResendOtp}
            >
              {resendCooldown > 0
                ? `Resend OTP in ${resendCooldown}s`
                : "Resend OTP"}
            </Button>
          </div>
        </form>
      ) : (
        /* ---------------- Step 3: set new password ---------------- */
        <form onSubmit={handleResetPassword} className="space-y-4">
          <Input
            label="New Password"
            name="password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            required
          />

          <div className="rounded-lg bg-slate-50 p-3">
            <p className="mb-1.5 text-xs font-medium text-slate-600">
              Password requirements
            </p>
            <ul className="space-y-0.5 text-xs">
              {passwordRequirements.map((req) => (
                <li
                  key={req.label}
                  className={req.met ? "text-green-600" : "text-red-600"}
                >
                  {req.met ? "✅" : "❌"} {req.label}
                </li>
              ))}
            </ul>
          </div>

          <Input
            label="Confirm Password"
            name="confirm_password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-type new password"
            autoComplete="new-password"
            required
          />

          {confirmTouched ? (
            <p
              className={
                passwordsMatch ? "text-sm text-green-600" : "text-sm text-red-600"
              }
            >
              {passwordsMatch ? "✅ Passwords match" : "❌ Passwords do not match"}
            </p>
          ) : null}

          <Button
            type="submit"
            className="w-full"
            loading={submitting}
            disabled={!isPasswordValid || !passwordsMatch}
          >
            Reset Password
          </Button>
        </form>
      )}

      <p className="text-center text-sm text-slate-500">
        Remember your password?{" "}
        <button
          type="button"
          onClick={() => navigate(ROUTES.LOGIN)}
          className="font-medium text-brand-600 hover:text-brand-700"
        >
          Back to login
        </button>
      </p>
    </div>
  );
}
