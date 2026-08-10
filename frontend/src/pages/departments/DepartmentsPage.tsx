/**
 * DepartmentsPage.
 * Department list + create/edit/delete UI.
 */

import { useEffect, useState } from "react";
import { useDepartments } from "@/hooks/useDepartments";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { Loader } from "@/components/common/Loader";
import { cn } from "@/utils/helpers";
import { Department } from "@/types/department";

// Roles allowed to manage departments fully.
const MANAGE_ROLES = ["ADMIN", "SUPER_ADMIN"];

// Empty form shape.
const EMPTY_FORM = {
  name: "",
  code: "",
  description: "",
};

export function DepartmentsPage() {
  const { departments, loading, error, list, create, update, remove } =
    useDepartments();
  const { user } = useAuth();

  const canManage =
    user?.role && MANAGE_ROLES.includes(user.role.toUpperCase());

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Department | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    list();
  }, [list]);

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (dept: Department) => {
    setEditing(dept);
    setForm({
      name: dept.name,
      code: dept.code,
      description: dept.description || "",
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      if (editing) {
        await update(editing.department_id, {
          name: form.name,
          code: form.code,
          description: form.description,
        });
      } else {
        await create({
          name: form.name,
          code: form.code,
          description: form.description,
        });
      }
      setModalOpen(false);
      await list();
    } catch (err) {
      setFormError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Something went wrong."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (dept: Department) => {
    if (!window.confirm(`Delete department "${dept.name}"?`)) return;
    try {
      await remove(dept.department_id);
      await list();
    } catch {
      // handled by slice error state
    }
  };

  return (
    <div>
      <PageHeader
        title="Departments"
        subtitle="Manage the departments in your organization."
        actions={
          canManage ? (
            <Button onClick={openCreate}>New department</Button>
          ) : undefined
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      {loading && departments.length === 0 ? (
        <Loader />
      ) : departments.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No departments yet. Create your first department.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Code</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Description</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                {canManage ? (
                  <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {departments.map((dept) => (
                <tr key={dept.department_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{dept.name}</td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                      {dept.code}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{dept.description || "—"}</td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                        dept.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-slate-100 text-slate-600"
                      )}
                    >
                      {dept.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  {canManage ? (
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEdit(dept)}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(dept)}
                          className="rounded border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  ) : null}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editing ? "Edit department" : "New department"}
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError ? (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
          ) : null}

          <Input
            label="Name"
            name="name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />

          <Input
            label="Code"
            name="code"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            hint="Short unique code, e.g. ENG"
            required
          />

          <Input
            label="Description (optional)"
            name="description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              {editing ? "Save changes" : "Create department"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
