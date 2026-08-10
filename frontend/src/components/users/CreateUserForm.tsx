/**
 * CreateUserForm.
 * Form for a privileged user to create an Admin, HR Manager, or Employee
 * account. The selectable roles are limited based on the current user's role.
 */

import { useState } from "react";
import { userService } from "@/services/user.service";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { getErrorMessage } from "@/utils/helpers";
import { ROLES } from "@/utils/constants";

const ROLE_OPTIONS = [
  { value: ROLES.ADMIN, label: "Admin" },
  { value: ROLES.HR_MANAGER, label: "HR Manager" },
  { value: ROLES.EMPLOYEE, label: "Employee" },
];

/** Which roles the current role may create. */
const CREATEABLE_ROLES: Record<string, string[]> = {
  [ROLES.SUPER_ADMIN]: [ROLES.ADMIN, ROLES.HR_MANAGER, ROLES.EMPLOYEE],
  [ROLES.ADMIN]: [ROLES.HR_MANAGER, ROLES.EMPLOYEE],
  [ROLES.HR_MANAGER]: [ROLES.EMPLOYEE],
};

interface CreateUserFormProps {
  actorRole?: string | null;
  onSuccess: (userId: string) => void;
}

export function CreateUserForm({ actorRole, onSuccess }: CreateUserFormProps) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<string>(ROLES.EMPLOYEE);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const allowedRoles = CREATEABLE_ROLES[actorRole || ""] || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const result = await userService.createUser({
        first_name: firstName,
        last_name: lastName,
        email,
        phone,
        password,
        role,
      });
      onSuccess(result.user_id);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (allowedRoles.length === 0) {
    return (
      <div className="rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
        You do not have permission to create users.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error ? (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="First name"
          name="firstName"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <Input
          label="Last name"
          name="lastName"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </div>

      <Input
        label="Email"
        name="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@company.com"
        autoComplete="email"
        required
      />

      <Input
        label="Phone (optional)"
        name="phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />

      <div>
        <label className="label" htmlFor="role">
          Role
        </label>
        <select
          id="role"
          name="role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="input"
          required
        >
          {ROLE_OPTIONS.filter((opt) => allowedRoles.includes(opt.value)).map(
            (opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            )
          )}
        </select>
      </div>

      <Input
        label="Password"
        name="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="At least 8 characters"
        autoComplete="new-password"
        required
      />

      <Button type="submit" className="w-full" loading={submitting}>
        Create user
      </Button>
    </form>
  );
}
