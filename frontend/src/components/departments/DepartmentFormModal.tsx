/**
 * DepartmentFormModal.
 *
 * Reusable modal for creating and editing departments.
 */

import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Department } from "@/types/department";

interface DepartmentFormModalProps {
  open: boolean;
  editing: Department | null;
  form: {
    name: string;
    code: string;
    description: string;
    is_active: boolean;
  };
  submitting: boolean;
  formError: string | null;
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  onFormChange: (field: string, value: string | boolean) => void;
}

export function DepartmentFormModal({
  open,
  editing,
  form,
  submitting,
  formError,
  onClose,
  onSubmit,
  onFormChange,
}: DepartmentFormModalProps) {
  return (
    <Modal
      open={open}
      title={editing ? "Edit department" : "New department"}
      onClose={onClose}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {formError ? (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
        ) : null}

        <Input
          label="Name"
          name="name"
          value={form.name}
          onChange={(e) => onFormChange("name", e.target.value)}
          required
        />

        <Input
          label="Code"
          name="code"
          value={form.code}
          onChange={(e) => onFormChange("code", e.target.value)}
          hint="Short unique code, e.g. ENG"
          required
        />

        <Input
          label="Description (optional)"
          name="description"
          value={form.description}
          onChange={(e) => onFormChange("description", e.target.value)}
        />

        <div>
          <label className="label" htmlFor="is_active">
            Status
          </label>
          <select
            id="is_active"
            name="is_active"
            value={form.is_active ? "true" : "false"}
            onChange={(e) => onFormChange("is_active", e.target.value === "true")}
            className="input"
          >
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            {editing ? "Save changes" : "Create department"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
