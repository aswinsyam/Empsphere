/**
 * LoginPage.
 *
 * Public authentication page. Provides a centered card containing the
 * `LoginForm` component, wrapped in the application's branding and
 * responsive background.
 */

import { LoginForm } from "@/components/auth/LoginForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function LoginPage() {
  return (
    <AuthPageShell title="Sign in to your employee account">
      <LoginForm />
    </AuthPageShell>
  );
}
