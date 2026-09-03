/**
 * LoginForm.
 *
 * Handles email/password authentication and Google sign-in.
 * On success it navigates to the role-specific dashboard. If the
 * backend indicates OTP is required (e.g. first login or email
 * verification), it redirects to the verify-email page.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { GoogleAuthButton } from "@/components/auth/GoogleAuthButton";
import { getErrorMessage } from "@/utils/helpers";
import { getDashboardRoute, ROUTES } from "@/utils/constants";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

export function LoginForm() {
  /**
   * Email/password and Google login form. On success it navigates to
   * the role-specific dashboard. If OTP is required, it redirects to
   * the email verification page.
   */
  const { login, googleLogin, loading } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const result = await login({ email, password }).unwrap();

      if (result.requires_otp) {
        toastSuccess(AuthToasts.otpSent);
        const purpose = result.purpose || "";
        navigate(
          `/verify-email?email=${encodeURIComponent(email)}${purpose ? `&purpose=${purpose}` : ""}`,
          { replace: true }
        );
        return;
      }

      toastSuccess("Login successful.");
      const role = result.role;
      navigate(getDashboardRoute(role), { replace: true });
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    }
  };

  // Exchange the Google credential for an EmpSphere JWT and go to the dashboard.
  const handleGoogleCredential = async (credential: string) => {
    try {
      const result = await googleLogin(credential).unwrap();

      if (result.requires_otp) {
        toastSuccess(AuthToasts.otpSent);
        const purpose = result.purpose || "";
        navigate(
          `/verify-email?email=${encodeURIComponent(result.email)}${purpose ? `&purpose=${purpose}` : ""}`,
          { replace: true }
        );
        return;
      }

      toastSuccess("Login successful.");
      const role = result.role;
      navigate(getDashboardRoute(role), { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {/* Email + password login */}
      <form onSubmit={handlePasswordSubmit} className="space-y-4">
        <Input
          label="Email / User ID"
          name="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          autoComplete="email"
          required
        />

        <Input
          label="Password"
          name="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          autoComplete="current-password"
          required
        />

        <div className="flex items-center justify-between text-sm">
          <Link
            to={ROUTES.FORGOT_PASSWORD}
            className="font-medium text-brand-600 hover:text-brand-700"
          >
            Forgot password?
          </Link>
        </div>

        <Button type="submit" className="w-full" loading={loading}>
          Login
        </Button>
      </form>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-slate-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-slate-500">or</span>
        </div>
      </div>

      {/* Continue with Google */}
      <GoogleAuthButton onCredential={handleGoogleCredential} />

      <p className="text-center text-sm text-slate-500">
        Don't have an account?{" "}
        <Link
          to="/register"
          className="font-medium text-brand-600 hover:text-brand-700"
        >
          Register
        </Link>
      </p>
    </div>
  );
}