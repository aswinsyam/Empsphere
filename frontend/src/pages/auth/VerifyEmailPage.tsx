/**
 * VerifyEmailPage.
 * Lets a user enter an OTP sent to their email to verify their account,
 * with the option to resend the OTP.
 */

import { useSearchParams } from "react-router-dom";
import { VerifyEmailForm } from "@/components/auth/VerifyEmailForm";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">EmpSphere</h1>
          <p className="mt-2 text-sm text-slate-500">
            Verify your email address
          </p>
        </div>

        <div className="card p-6">
          <VerifyEmailForm email={email} />
        </div>
      </div>
    </div>
  );
}
