/**
 * LoginPage.
 * Public login screen.
 */

import { Link } from "react-router-dom";
import { LoginForm } from "@/components/auth/LoginForm";

export function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">EmpSphere</h1>
          <p className="mt-2 text-sm text-slate-500">
            Sign in to your employee account
          </p>
        </div>

        <div className="card p-6">
          <LoginForm />
        </div>

        <p className="mt-4 text-center text-sm text-slate-500">
          Don&apos;t have an account?{" "}
          <Link
            to="/register"
            className="font-medium text-brand-600 hover:text-brand-700"
          >
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
