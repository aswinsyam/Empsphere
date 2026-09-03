/**
 * RegisterForm.
 *
 * New user registration form. Collects identity, contact, and password
 * details plus a company registration secret. Validates password
 * strength and confirmation before submitting. Supports Google sign-in
 * as an alternative.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { GoogleAuthButton } from "@/components/auth/GoogleAuthButton";
import { getErrorMessage, getPasswordRequirements } from "@/utils/helpers";
import { getDashboardRoute } from "@/utils/constants";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

export function RegisterForm() {
  /**
   * New account registration form. Validates password strength and
   * confirmation, collects a company registration secret, and supports
   * Google sign-in. On success, redirects to the email verification page.
   */
  const { register, googleLogin, loading } = useAuth();
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [companySecret, setCompanySecret] = useState("");
  const [error, setError] = useState<string | null>(null);

  const passwordRequirements = getPasswordRequirements(password);
  const isPasswordValid = passwordRequirements.every((req) => req.met);

  const confirmTouched = confirmPassword.length > 0;
  const passwordsMatch = password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isPasswordValid) {
      const msg = "Please meet all password requirements before registering.";
      setError(msg);
      toastError(msg);
      return;
    }

    if (!passwordsMatch) {
      const msg = "Passwords do not match.";
      setError(msg);
      toastError(msg);
      return;
    }

    try {
      await register({
        first_name: firstName,
        last_name: lastName,
        email,
        phone,
        password,
        confirm_password: confirmPassword,
        company_secret: companySecret,
      });
      toastSuccess(AuthToasts.registrationSuccess);
      navigate(`/verify-email?email=${encodeURIComponent(email)}`, {
        replace: true,
      });
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    }
  };

  // "Continue with Google": authenticate and go to the role dashboard.
  const handleGoogleCredential = (credential: string) => {
    googleLogin(credential)
      .then((result) => {
        const role = (result as { payload?: { role?: string } }).payload?.role;
        navigate(getDashboardRoute(role), { replace: true });
      })
      .catch((err) => setError(getErrorMessage(err)));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="First name"
          name="firstName"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <Input
          label="Last name"
          name="lastName"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </div>

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
        label="Phone (optional)"
        name="phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />

      <Input
        label="Password"
        name="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
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
        name="confirmPassword"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Re-type your password"
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

      <Input
        label="Company Registration Secret"
        name="companySecret"
        type="password"
        value={companySecret}
        onChange={(e) => setCompanySecret(e.target.value)}
        placeholder="Provided by your organization"
        autoComplete="off"
        required
      />

      <Button
        type="submit"
        className="w-full"
        loading={loading}
        disabled={!isPasswordValid || !passwordsMatch}
      >
        Create Admin Account
      </Button>

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
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
          Sign in
        </Link>
      </p>
    </form>
  );
}
