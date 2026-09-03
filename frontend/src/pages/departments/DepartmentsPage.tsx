/**
 * DepartmentsPage.
 *
 * Lists active departments in a table and lets SUPER_ADMIN / ADMIN /
 * HR_MANAGER create, edit, or soft-delete departments.
 */

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { departmentService } from "@/services/department.service";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { cn } from "@/utils/helpers";
import { Department } from "@/types/department";
import { DepartmentFormModal } from "@/components/departments/DepartmentFormModal";
import { canManageEmployees } from "@/utils/constants";
import { toastSuccess, toastApiError } from "@/components/common/ToastProvider";

const EMPTY_FORM = {
  name: "",
  code: "",
  description: "",
  is_active: true,
};

export function DepartmentsPage() {
  const { user } = useAuth();

  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [search, setSearch] = useState("");

  const canManage = canManageEmployees(user?.role);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Department | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [confirmStatus, setConfirmStatus] = useState<Department | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const loadDepartments = async (pageNum = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result = await departmentService.list({
        search: search || undefined,
        page: pageNum,
        page_size: 10,
        include_inactive: true,
      });
      setDepartments(result.departments);
      setPage(result.page);
      setTotalPages(result.total_pages);
      setTotalRecords(result.total_records);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load departments");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments(1);
  }, [search]);

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
      is_active: dept.is_active ?? true,
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
        await departmentService.update(editing.department_id, {
          name: form.name,
          code: form.code,
          description: form.description,
          is_active: form.is_active,
        });
        toastSuccess("Department updated successfully.");
      } else {
        await departmentService.create({
          name: form.name,
          code: form.code,
          description: form.description,
        });
        toastSuccess("Department created successfully.");
      }
      setModalOpen(false);
      await loadDepartments(1);
    } catch (err) {
      toastApiError(err, "Failed to save department");
      setFormError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  const confirmStatusToggle = async () => {
    if (!confirmStatus) return;
    const newStatus = !confirmStatus.is_active;
    setStatusLoading(true);
    try {
      await departmentService.update(confirmStatus.department_id, { is_active: newStatus });
      toastSuccess(newStatus ? "Department activated successfully." : "Department deactivated successfully.");
      setConfirmStatus(null);
      await loadDepartments(1);
    } catch (err) {
      toastApiError(err, newStatus ? "Failed to activate department" : "Failed to deactivate department");
    } finally {
      setStatusLoading(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Departments"
        subtitle="Manage the departments in your organization."
        actions={
          canManage ? (
            <Button onClick={openCreate}>Create Department</Button>
          ) : undefined
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end">
        <Input
          label="Search"
          name="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or code..."
          className="sm:max-w-xs"
        />
      </div>

      {loading && departments.length === 0 ? (
        <Loader />
      ) : departments.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No departments found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Code</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Description</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Employees</th>
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
                  <td className="px-4 py-3 text-slate-600">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                      {dept.code}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{dept.description || "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{dept.employee_count ?? 0}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={dept.is_active} />
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
                          onClick={() => setConfirmStatus(dept)}
                          className={cn(
                            "rounded border px-2 py-1 text-xs font-medium",
                            dept.is_active
                              ? "border-amber-200 text-amber-700 hover:bg-amber-50"
                              : "border-green-200 text-green-600 hover:bg-green-50"
                          )}
                        >
                          {dept.is_active ? "Deactivate" : "Activate"}
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

      {totalPages > 1 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          totalRecords={totalRecords}
          onPageChange={(nextPage) => loadDepartments(nextPage)}
        />
      )}

      <DepartmentFormModal
        open={modalOpen}
        editing={editing}
        form={form}
        submitting={submitting}
        formError={formError}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        onFormChange={(field, value) => setForm({ ...form, [field]: value })}
      />

      <Modal
        open={confirmStatus !== null}
        title={confirmStatus?.is_active ? "Deactivate department" : "Activate department"}
        onClose={() => setConfirmStatus(null)}
      >
        <p className="text-sm text-slate-600">
          {confirmStatus?.is_active
            ? `Deactivate department "${confirmStatus?.name}"? Existing data will be preserved.`
            : `Activate department "${confirmStatus?.name}"?`}
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setConfirmStatus(null)}>
            Cancel
          </Button>
          <Button variant={confirmStatus?.is_active ? "danger" : "primary"} loading={statusLoading} onClick={confirmStatusToggle}>
            {confirmStatus?.is_active ? "Deactivate" : "Activate"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
