/**
 * SetPasswordForm.
 *
 * For Google-authenticated users who do not have a local password.
 *
 * Flow:
 *   1. Click "Send OTP" — the backend sends an OTP to the user's
 *      verified email (derived from the session, not the request body).
 *   2. Enter the OTP, new password, and confirm password.
 *   3. Submit — the backend verifies the OTP and stores the password.
 *
 * This reuses the existing OTP infrastructure (purpose="password_setup").
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";
import { ROUTES } from "@/utils/constants";

export function SetPasswordForm() {
  const navigate = useNavigate();

  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSendOtp = async () => {
    setError(null);
    setSuccess(null);
    setSending(true);
    try {
      await authService.sendOtp({ purpose: "password_setup" });
      setOtpSent(true);
      setSuccess("OTP sent to your email.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return;
    }

    setLoading(true);
    try {
      await authService.setPassword({ otp, new_password: newPassword });
      setSuccess("Password set successfully. You can now log in with your password.");
      setTimeout(() => navigate(ROUTES.LOGIN, { replace: true }), 1500);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
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

      {!otpSent ? (
        <Button
          type="button"
          className="w-full"
          loading={sending}
          onClick={handleSendOtp}
        >
          Send OTP
        </Button>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="OTP Code"
            name="otp"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit code"
            autoComplete="one-time-password"
            required
          />

          <Input
            label="New Password"
            name="newPassword"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            required
          />

          <Input
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-type new password"
            autoComplete="new-password"
            required
          />

          <Button type="submit" className="w-full" loading={loading}>
            Set Password
          </Button>
        </form>
      )}
    </div>
  );
}