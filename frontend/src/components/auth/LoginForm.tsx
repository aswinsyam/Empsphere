/**
 * LoginForm.
 * Email + password login form with OTP and Google options.
 */

import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";
import { getDashboardRoute } from "@/utils/constants";
import { ENV } from "@/config/env";

/** Google Identity Services account ID API surface. */
interface GoogleAccountsId {
  initialize: (config: {
    client_id: string;
    callback: (response: { credential: string }) => void;
  }) => void;
  prompt: (listener?: () => void) => void;
  renderButton: (
    parent: HTMLElement,
    options?: Record<string, unknown>
  ) => void;
}

/** Minimal shape of the global `google` object injected by the GSI script. */
interface GoogleGlobal {
  accounts?: { id?: GoogleAccountsId };
}

/** Shape of `window` augmented with the GSI `google` global. */
interface WindowWithGoogle extends Window {
  google?: GoogleGlobal;
}

type LoginTab = "password" | "otp" | "google";

export function LoginForm() {
  const { login, googleLogin, loading } = useAuth();
  const navigate = useNavigate();
  const googleButtonContainerRef = useRef<HTMLDivElement>(null);

  const [activeTab, setActiveTab] = useState<LoginTab>("password");

  // Password login state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // OTP login state
  const [otpEmail, setOtpEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  const [otpSubmitting, setOtpSubmitting] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [googleError, setGoogleError] = useState<string | null>(null);

  // Password login handler
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const result = await login({ email, password });
      const role = (result as { payload?: { role?: string } }).payload?.role;
      navigate(getDashboardRoute(role), { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  // OTP login handlers
  const handleSendOtp = async () => {
    setError(null);
    setOtpLoading(true);
    try {
      await authService.sendOtp({ email: otpEmail, purpose: "login" });
      setOtpSent(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setOtpLoading(false);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prevent duplicate submissions
    if (otpSubmitting) {
      return;
    }
    
    setError(null);
    setOtpSubmitting(true);
    try {
      const result = await authService.loginWithOtp(otpEmail, otp);
      const role = (result as { role?: string }).role;
      navigate(getDashboardRoute(role), { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setOtpSubmitting(false);
    }
  };

  // Render the official Google sign-in button when Google tab is active.
  useEffect(() => {
    if (activeTab !== "google") {
      return;
    }

    const clientId = ENV.GOOGLE_CLIENT_ID;

    if (!clientId) {
      setGoogleError(
        "Google login is not configured. Set VITE_GOOGLE_CLIENT_ID in frontend/.env and GOOGLE_CLIENT_ID in backend/.env."
      );
      return;
    }

    const google = (window as unknown as WindowWithGoogle).google;
    const id = google?.accounts?.id;

    if (!id) {
      setGoogleError(
        "Google Identity Services failed to load. Check your internet connection and try again."
      );
      return;
    }

    // One-time callback that exchanges the Google credential for an
    // EmpSphere JWT, stores tokens, and redirects to the role dashboard.
    const handleCredential = (response: { credential: string }) => {
      googleLogin(response.credential)
        .then((result) => {
          const role = (result as { payload?: { role?: string } }).payload?.role;
          navigate(getDashboardRoute(role), { replace: true });
        })
        .catch((err) => setError(getErrorMessage(err)));
    };

    id.initialize({ client_id: clientId, callback: handleCredential });

    if (googleButtonContainerRef.current) {
      id.renderButton(googleButtonContainerRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        width: "100%",
        text: "continue_with",
      });
    }
  }, [googleLogin, navigate, activeTab]);

  return (
    <div className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {/* Tab buttons */}
      <div className="flex rounded-lg bg-slate-100 p-1">
        <button
          type="button"
          onClick={() => setActiveTab("password")}
          className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === "password"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Password
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("otp")}
          className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === "otp"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          OTP
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("google")}
          className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === "google"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Google
        </button>
      </div>

      {/* Password login form */}
      {activeTab === "password" && (
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
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
              to="/forgot-password"
              className="font-medium text-brand-600 hover:text-brand-700"
            >
              Forgot password?
            </Link>
          </div>

          <Button type="submit" className="w-full" loading={loading}>
            Sign in
          </Button>
        </form>
      )}

      {/* OTP login form */}
      {activeTab === "otp" && (
        <div className="space-y-4">
          {!otpSent ? (
            <>
              <Input
                label="Email"
                name="otpEmail"
                type="email"
                value={otpEmail}
                onChange={(e) => setOtpEmail(e.target.value)}
                placeholder="you@company.com"
                autoComplete="email"
                required
              />
              <Button
                type="button"
                className="w-full"
                loading={otpLoading}
                onClick={handleSendOtp}
              >
                Send OTP
              </Button>
            </>
          ) : (
            <form onSubmit={handleOtpSubmit} className="space-y-4">
              <Input
                label="OTP Code"
                name="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="6-digit code"
                autoComplete="one-time-password"
                required
              />
              <Button type="submit" className="w-full" loading={otpSubmitting || loading}>
                Sign in with OTP
              </Button>
            </form>
          )}
        </div>
      )}

      {/* Google login */}
      {activeTab === "google" && (
        <div className="space-y-4">
          {googleError ? (
            <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-700">
              {googleError}
            </div>
          ) : (
            <div
              ref={googleButtonContainerRef}
              className="flex justify-center"
              aria-label="Continue with Google"
            />
          )}
        </div>
      )}

      <p className="text-center text-sm text-slate-500">
        Don't have an account?{" "}
        <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
          Sign up
        </Link>
      </p>
    </div>
  );
}