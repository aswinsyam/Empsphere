/**
 * VerifyEmailPage.
 *
 * Reads `email` and optional `purpose` query parameters and passes them
 * to `VerifyEmailForm`. Supports both initial verification and OTP-based
 * flows such as first-login or password-setup verification.
 */

import { useSearchParams } from "react-router-dom";
import { VerifyEmailForm } from "@/components/auth/VerifyEmailForm";
import { AuthPageShell } from "@/components/auth/AuthPageShell";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";
  const purpose = searchParams.get("purpose") || undefined;

  return (
    <AuthPageShell title="Verify your email address">
      <VerifyEmailForm email={email} purpose={purpose} />
    </AuthPageShell>
  );
}
