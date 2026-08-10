/**
 * RegisterPage.
 * Public registration screen.
 */

import { RegisterForm } from "@/components/auth/RegisterForm";

export function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">EmpSphere</h1>
          <p className="mt-2 text-sm text-slate-500">
            Create your admin account
          </p>
        </div>

        <div className="card p-6">
          <RegisterForm />
        </div>
      </div>
    </div>
  );
}
