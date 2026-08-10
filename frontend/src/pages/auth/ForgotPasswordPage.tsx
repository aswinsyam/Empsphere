/**
 * ForgotPasswordPage.
 * Public forgot-password screen.
 */

import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";

export function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">EmpSphere</h1>
          <p className="mt-2 text-sm text-slate-500">Reset your password</p>
        </div>

        <div className="card p-6">
          <ForgotPasswordForm />
        </div>
      </div>
    </div>
  );
}
