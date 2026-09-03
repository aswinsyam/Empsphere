/**
 * ChangePasswordPage.
 *
 * Protected page that renders the `ChangePasswordForm` with a page header.
 * Accessible to any authenticated user who wants to update their password.
 */

import { ChangePasswordForm } from "@/components/auth/ChangePasswordForm";
import { PageHeader } from "@/components/common/PageHeader";

export function ChangePasswordPage() {
  /**
   * Protected page with a header and `ChangePasswordForm`. Accessible
   * to any authenticated user who wants to update their password.
   */
  return (
    <div className="mx-auto max-w-xl">
      <PageHeader
        title="Change Password"
        subtitle="Update your account password to keep your account secure."
      />
      <div className="card p-6">
        <ChangePasswordForm />
      </div>
    </div>
  );
}
