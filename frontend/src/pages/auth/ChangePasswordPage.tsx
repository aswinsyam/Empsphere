/**
 * ChangePasswordPage.
 * Protected screen for updating the current user's password.
 */

import { ChangePasswordForm } from "@/components/auth/ChangePasswordForm";
import { PageHeader } from "@/components/common/PageHeader";

export function ChangePasswordPage() {
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
