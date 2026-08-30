/**
 * ResetPasswordPage.
 *
 * Public page for users to reset their password using an OTP.
 */

import { useSearchParams } from "react-router-dom";
import { ResetPasswordForm } from "@/components/auth/ResetPasswordForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";

  return (
    <AuthPageShell title="Reset your password">
      <ResetPasswordForm email={email} />
    </AuthPageShell>
  );
}
