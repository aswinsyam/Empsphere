/**
 * SetPasswordPage.
 *
 * Public page for Google-authenticated users who lack a local password.
 * Uses OTP verification (`purpose="password_setup"`) to let the user set
 * a new password before they can sign in with email and password.
 */

import { SetPasswordForm } from "@/components/auth/SetPasswordForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function SetPasswordPage() {
  return (
    <AuthPageShell title="Set a password for your account">
      <SetPasswordForm />
    </AuthPageShell>
  );
}