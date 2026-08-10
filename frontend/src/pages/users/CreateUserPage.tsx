/**
 * CreateUserPage.
 * Protected page where privileged users create Admin/HR/Employee accounts.
 */

import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { CreateUserForm } from "@/components/users/CreateUserForm";
import { PageHeader } from "@/components/common/PageHeader";

export function CreateUserPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

// `userId` is passed by the form's onSuccess callback; it is intentionally
// unused here because the page simply redirects after a successful creation.
const handleSuccess = (_userId: string) => {
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader
        title="Create user"
        subtitle="Add an Admin, HR Manager, or Employee account."
      />
      <div className="card p-6">
        <CreateUserForm actorRole={user?.role} onSuccess={handleSuccess} />
      </div>
    </div>
  );
}
