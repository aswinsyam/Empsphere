/**
 * VerifyEmailForm.
 *
 * OTP verification component used for email verification, first-login
 * completion, and password-setup flows. Accepts an optional `email` and
 * `purpose` prop. Manages a 30-second resend cooldown and dispatches
 * Redux actions for first-login completion.
 *
 * @param email - Pre-filled email address (fallback to empty string).
 * @param purpose - Optional OTP purpose (`first_login`, `password_setup`, etc.).
 */

import { useNavigate } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { useDispatch } from "react-redux";
import { AppDispatch } from "@/store";
import { authService } from "@/services/auth.service";
import { completeFirstLogin, setUser, normalizeUser } from "@/store/slices/authSlice";
import { TokenUtil } from "@/utils/token";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";
import { getDashboardRoute } from "@/utils/constants";
import {
  SendOTPPayload,
  VerifyOTPPayload,
} from "@/types/auth";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

const RESEND_COOLDOWN_SECONDS = 30;

interface VerifyEmailFormProps {
  email?: string;
  purpose?: string;
}

export function VerifyEmailForm({ email = "", purpose }: VerifyEmailFormProps) {
  /**
   * OTP verification form. Handles sending and verifying OTPs for
   * email verification, first-login completion, and password-setup.
   * Enforces a 30-second resend cooldown.
   */
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const [emailValue, setEmailValue] = useState(email);
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sending, setSending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

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

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSending(true);
    try {
      await authService.sendOtp({
        email: emailValue,
        ...(purpose ? { purpose: purpose as SendOTPPayload["purpose"] } : {}),
      });
      setMessage("OTP sent. Please check your inbox.");
      toastSuccess(AuthToasts.otpSent);
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setSending(false);
    }
  };

  const handleResendOtp = useCallback(async () => {
    if (resendCooldown > 0 || sending) return;
    setError(null);
    setMessage(null);
    setSending(true);
    try {
      await authService.sendOtp({
        email: emailValue,
        ...(purpose ? { purpose: purpose as SendOTPPayload["purpose"] } : {}),
      });
      setMessage("OTP resent. Please check your inbox.");
      toastSuccess(AuthToasts.otpSent);
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setSending(false);
    }
  }, [resendCooldown, sending, emailValue, purpose]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSubmitting(true);
    try {
      if (purpose === "first_login") {
        const result = await dispatch(
          completeFirstLogin({
            email: emailValue,
            otp,
            purpose: purpose as VerifyOTPPayload["purpose"],
          })
        ).unwrap();
        toastSuccess(AuthToasts.otpVerified);
        navigate(getDashboardRoute(result.role), { replace: true });
      } else {
        const result = await authService.verifyOtp({
          email: emailValue,
          otp,
          ...(purpose ? { purpose: purpose as VerifyOTPPayload["purpose"] } : {}),
        });
        toastSuccess(AuthToasts.otpVerified);
        if (result.access_token && result.refresh_token) {
          TokenUtil.setTokens(result.access_token, result.refresh_token);
        }
        if (result.user_id) {
          dispatch(setUser(normalizeUser(result)));
        }
        navigate(getDashboardRoute(result.role), { replace: true });
      }
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      {message ? (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      ) : null}

      {/* Send OTP */}
      <form onSubmit={handleSendOtp} className="space-y-4">
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
        <Button type="submit" className="w-full" variant="ghost" loading={sending}>
          Send OTP
        </Button>
      </form>

      <div className="border-t border-slate-200 pt-6">
        <form onSubmit={handleVerify} className="space-y-4">
          <Input
            label="Verification code"
            name="otp"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit code"
            inputMode="numeric"
            maxLength={6}
            required
          />
          <Button type="submit" className="w-full" loading={submitting}>
            Verify email
          </Button>
          <div className="text-center">
            <Button
              type="button"
              variant="ghost"
              className="text-sm"
              loading={sending}
              disabled={resendCooldown > 0}
              onClick={handleResendOtp}
            >
              {resendCooldown > 0
                ? `Resend OTP in ${resendCooldown}s`
                : "Resend OTP"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
