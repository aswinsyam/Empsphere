/**
 * EmployeeFormModal.
 *
 * Reusable modal for creating and editing employees.
 */

import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Employee } from "@/types/employee";
import { Department } from "@/types/department";
import { Designation } from "@/types/designation";

interface EmployeeFormModalProps {
  open: boolean;
  editing: Employee | null;
  departments: Department[];
  designations: Designation[];
  form: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    role: string;
    department_id: string;
    designation_id: string;
    joining_date: string;
    status: string;
    password: string;
  };
  submitting: boolean;
  formError: string | null;
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  onFormChange: (field: string, value: string) => void;
}

export function EmployeeFormModal({
  open,
  editing,
  departments,
  designations,
  form,
  submitting,
  formError,
  onClose,
  onSubmit,
  onFormChange,
}: EmployeeFormModalProps) {
  return (
    <Modal
      open={open}
      title={editing ? "Edit employee" : "New employee"}
      onClose={onClose}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {formError ? (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
        ) : null}

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="First name"
            name="first_name"
            value={form.first_name}
            onChange={(e) => onFormChange("first_name", e.target.value)}
            required
          />
          <Input
            label="Last name"
            name="last_name"
            value={form.last_name}
            onChange={(e) => onFormChange("last_name", e.target.value)}
            required
          />
        </div>

        <Input
          label="Email"
          name="email"
          type="email"
          value={form.email}
          onChange={(e) => onFormChange("email", e.target.value)}
          required
        />

        {!editing && (
          <Input
            label="Password"
            name="password"
            type="password"
            value={form.password}
            onChange={(e) => onFormChange("password", e.target.value)}
            placeholder="Set initial password"
            required={!editing}
          />
        )}

        <Input
          label="Phone (optional)"
          name="phone"
          value={form.phone}
          onChange={(e) => onFormChange("phone", e.target.value)}
        />

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label" htmlFor="role">
              Role
            </label>
            <select
              id="role"
              name="role"
              value={form.role}
              onChange={(e) => onFormChange("role", e.target.value)}
              className="input"
            >
              <option value="EMPLOYEE">Employee</option>
              <option value="HR_MANAGER">HR Manager</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="status">
              Status
            </label>
            <select
              id="status"
              name="status"
              value={form.status}
              onChange={(e) => onFormChange("status", e.target.value)}
              className="input"
            >
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label" htmlFor="department_id">
              Department (optional)
            </label>
            <select
              id="department_id"
              name="department_id"
              value={form.department_id}
              onChange={(e) => onFormChange("department_id", e.target.value)}
              className="input"
            >
              <option value="">None</option>
              {departments.map((dept) => (
                <option key={dept.department_id} value={dept.department_id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="designation_id">
              Designation (optional)
            </label>
            <select
              id="designation_id"
              name="designation_id"
              value={form.designation_id}
              onChange={(e) => onFormChange("designation_id", e.target.value)}
              className="input"
            >
              <option value="">None</option>
              {designations.map((desig) => (
                <option key={desig.designation_id} value={desig.designation_id}>
                  {desig.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <Input
          label="Joining Date"
          name="joining_date"
          type="date"
          value={form.joining_date}
          onChange={(e) => onFormChange("joining_date", e.target.value)}
        />

        <div className="flex justify-end gap-2 pt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            {editing ? "Save changes" : "Create employee"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
