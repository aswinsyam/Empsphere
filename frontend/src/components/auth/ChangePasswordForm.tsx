/**
 * ChangePasswordForm.
 *
 * Allows an authenticated user to update their password. Requires the
 * current password plus a new password that meets the application's
 * strength requirements. Navigates to the dashboard on success.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { userService } from "@/services/user.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage, getPasswordRequirements } from "@/utils/helpers";
import { toastSuccess, toastError, AuthToasts } from "@/components/common/ToastProvider";

export function ChangePasswordForm() {
  /**
   * Allows an authenticated user to update their password. Requires
   * the current password and a new password that meets the application's
   * strength requirements. Navigates to the dashboard on success.
   */
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const passwordRequirements = getPasswordRequirements(newPassword);
  const isPasswordValid = passwordRequirements.every((req) => req.met);

  const confirmTouched = confirmPassword.length > 0;
  const passwordsMatch = newPassword === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!isPasswordValid) {
      const msg = "Please meet all password requirements before changing your password.";
      setError(msg);
      toastError(msg);
      return;
    }

    if (!passwordsMatch) {
      const msg = "New password and confirmation do not match.";
      setError(msg);
      toastError(msg);
      return;
    }

    setLoading(true);
    try {
      await userService.changePassword(currentPassword, newPassword);
      toastSuccess(AuthToasts.passwordChanged);
      setSuccess("Password changed successfully.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      toastError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {success ? (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      ) : null}

      <Input
        label="Current password"
        name="currentPassword"
        type="password"
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
        placeholder="••••••••"
        autoComplete="current-password"
        required
      />

      <Input
        label="New password"
        name="newPassword"
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
        label="Confirm new password"
        name="confirmPassword"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Re-enter new password"
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
        loading={loading}
        disabled={!isPasswordValid || !passwordsMatch}
      >
        Update password
      </Button>
    </form>
  );
}
