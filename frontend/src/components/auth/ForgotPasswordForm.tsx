/**
 * ForgotPasswordForm.
 *
 * Step 1 of the forgot-password flow: the user submits their registered
 * email and the backend sends a `forgot_password` OTP. The response is
 * intentionally identical whether or not an account exists, so it can
 * not be used to discover registered emails.
 *
 * On success the user is sent to the reset-password screen where the OTP
 * is verified and the new password is set.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";
import { ROUTES } from "@/utils/constants";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

export function ForgotPasswordForm() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await authService.forgotPassword({ email });
      setSuccess("OTP sent to your email. Please check your inbox.");
      toastSuccess(AuthToasts.otpSent);
      setTimeout(() => {
        navigate(`${ROUTES.RESET_PASSWORD}?email=${encodeURIComponent(email)}`, {
          replace: true,
        });
      }, 1200);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
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

      <p className="text-sm text-slate-500">
        Enter your registered email and we'll send you a one-time code to
        reset your password.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Email"
          name="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          autoComplete="email"
          required
        />
        <Button type="submit" className="w-full" loading={loading}>
          Send OTP
        </Button>
      </form>

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
