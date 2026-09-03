/**
 * ForgotPasswordPage.
 *
 * Public page for users to request a password reset OTP.
 */

import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function ForgotPasswordPage() {
  return (
    <AuthPageShell title="Reset your password">
      <ForgotPasswordForm />
    </AuthPageShell>
  );
}
