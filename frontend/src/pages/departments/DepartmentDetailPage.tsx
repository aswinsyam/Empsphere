import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { departmentService } from "@/services/department.service";
import { employeeService } from "@/services/employee.service";
import { useAuth } from "@/hooks/useAuth";
import { useDepartments } from "@/hooks/useDepartments";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Loader } from "@/components/common/Loader";
import { Modal } from "@/components/common/Modal";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/utils/helpers";
import { Department } from "@/types/department";
import { Employee } from "@/types/employee";
import { DepartmentFormModal } from "@/components/departments/DepartmentFormModal";
import { canManageEmployees } from "@/utils/constants";
import { toastSuccess, toastApiError } from "@/components/common/ToastProvider";

const EMPTY_FORM = {
  name: "",
  code: "",
  description: "",
  is_active: true,
};

export function DepartmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { update: updateDepartment } = useDepartments();
  const [department, setDepartment] = useState<Department | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [employeesLoading, setEmployeesLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Department | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [confirmStatus, setConfirmStatus] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const canManage = canManageEmployees(user?.role);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    departmentService
      .getById(id)
      .then((data) => setDepartment(data as Department))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load department."))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!id) return;
    setEmployeesLoading(true);
    employeeService
      .list({ department_id: id, page: 1, page_size: 50 })
      .then((data) => setEmployees(data.employees))
      .catch(() => setEmployees([]))
      .finally(() => setEmployeesLoading(false));
  }, [id]);

  const handleBack = () => navigate("/departments");

  const handleEdit = () => {
    if (!department) return;
    setEditing(department);
    setForm({
      name: department.name,
      code: department.code,
      description: department.description || "",
      is_active: department.is_active ?? true,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    setFormError(null);
    setSubmitting(true);
    try {
      await updateDepartment(editing.department_id, {
        name: form.name,
        code: form.code,
        description: form.description,
        is_active: form.is_active,
      });
      toastSuccess("Department updated successfully.");
      setModalOpen(false);
      if (id) {
        departmentService.getById(id).then((data) => setDepartment(data as Department));
      }
    } catch (err) {
      toastApiError(err, "Failed to update department");
      setFormError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Something went wrong."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const confirmStatusToggle = async () => {
    if (!department) return;
    const newStatus = !department.is_active;
    setDeleting(true);
    try {
      await updateDepartment(department.department_id, { is_active: newStatus });
      toastSuccess(newStatus ? "Department activated successfully." : "Department deactivated successfully.");
      setConfirmStatus(false);
      departmentService.getById(id!).then((data) => setDepartment(data as Department));
    } catch (err) {
      toastApiError(err, newStatus ? "Failed to activate department" : "Failed to deactivate department");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <Loader />;

  if (error || !department) {
    return (
      <div>
        <PageHeader title="Department Details" />
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error || "Department not found."}
        </div>
        <Button onClick={handleBack} variant="ghost" className="mt-4">
          Back to Departments
        </Button>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Department Details"
        subtitle={`Viewing details for ${department.name}`}
        actions={
          canManage ? (
            <div className="flex gap-2">
              <Button onClick={handleBack} variant="ghost">
                Back
              </Button>
              <Button onClick={handleEdit}>Edit Department</Button>
              <Button
                variant={department.is_active ? "danger" : "primary"}
                onClick={() => setConfirmStatus(true)}
              >
                {department.is_active ? "Deactivate" : "Activate"}
              </Button>
            </div>
          ) : (
            <Button onClick={handleBack} variant="ghost">
              Back
            </Button>
          )
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-slate-900">{department.name}</h3>
            <p className="mt-1 text-sm text-slate-500">{department.code}</p>
            <div className="mt-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Description</p>
              <p className="mt-1 text-sm text-slate-900">{department.description || "-"}</p>
            </div>
            <div className="mt-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Total Employees</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">{department.employee_count}</p>
            </div>
            <div className="mt-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Status</p>
              <StatusBadge status={department.is_active} />
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="card p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">Employees in this Department</h3>
            {employeesLoading ? (
              <Loader />
            ) : employees.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-500">
                No employees found in this department.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-slate-500">Employee ID</th>
                      <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                      <th className="px-4 py-3 text-left font-medium text-slate-500">Email</th>
                      <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      <th className="px-4 py-3 text-left font-medium text-slate-500">Joining Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {employees.map((emp) => (
                      <tr key={emp.user_id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 text-slate-600">{emp.employee_code || "-"}</td>
                        <td className="px-4 py-3 font-medium text-slate-900">
                          {emp.first_name} {emp.last_name}
                        </td>
                        <td className="px-4 py-3 text-slate-600">{emp.email}</td>
                        <td className="px-4 py-3">
                          <StatusBadge status={emp.status} />
                        </td>
                        <td className="px-4 py-3 text-slate-600">{formatDate(emp.joining_date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

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
        open={confirmStatus}
        title={department?.is_active ? "Deactivate department" : "Activate department"}
        onClose={() => setConfirmStatus(false)}
      >
        <p className="text-sm text-slate-600">
          {department?.is_active
            ? `Deactivate department "${department?.name}"? Existing data will be preserved.`
            : `Activate department "${department?.name}"?`}
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setConfirmStatus(false)}>
            Cancel
          </Button>
          <Button variant={department?.is_active ? "danger" : "primary"} loading={deleting} onClick={confirmStatusToggle}>
            {department?.is_active ? "Deactivate" : "Activate"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
