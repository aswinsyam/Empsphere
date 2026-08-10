/**
 * SetPasswordPage.
 *
 * For Google-authenticated users who do not have a local password.
 * Allows them to set a password using OTP verification.
 */

import { SetPasswordForm } from "@/components/auth/SetPasswordForm";

export function SetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">EmpSphere</h1>
          <p className="mt-2 text-sm text-slate-500">
            Set a password for your account
          </p>
        </div>

        <div className="card p-6">
          <SetPasswordForm />
        </div>
      </div>
    </div>
  );
}