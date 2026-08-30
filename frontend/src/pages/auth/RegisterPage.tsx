/**
 * RegisterPage.
 *
 * Public registration page. Displays the `RegisterForm` inside a
 * centered, branded card for new admin account creation.
 */

import { RegisterForm } from "@/components/auth/RegisterForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function RegisterPage() {
  return (
    <AuthPageShell title="Create your admin account">
      <RegisterForm />
    </AuthPageShell>
  );
}
