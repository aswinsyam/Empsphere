/**
 * EmployeeDetailPage.
 *
 * Read-only view of a single employee for SUPER_ADMIN / ADMIN / HR_MANAGER,
 * with Edit handled by the reusable `EmployeeFormModal`. No delete action is
 * exposed here.
 */

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { employeeService } from "@/services/employee.service";
import { useEmployees } from "@/hooks/useEmployees";
import { useDepartments } from "@/hooks/useDepartments";
import { useDesignations } from "@/hooks/useDesignations";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/utils/helpers";
import { Employee } from "@/types/employee";
import { Department } from "@/types/department";
import { Designation } from "@/types/designation";
import { EmployeeFormModal } from "@/components/employees/EmployeeFormModal";
import { canManageEmployees, ROUTES } from "@/utils/constants";

const EMPTY_FORM = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  role: "EMPLOYEE",
  department_id: "",
  designation_id: "",
  joining_date: "",
  status: "ACTIVE",
  password: "",
};

export function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { update: updateEmployee } = useEmployees();
  const { departments, list: listDepartments } = useDepartments();
  const { designations, list: listDesignations } = useDesignations();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Employee | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const canManage = canManageEmployees(user?.role);

  useEffect(() => {
    listDepartments({ include_inactive: true });
    listDesignations({ include_inactive: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    employeeService
      .getById(id)
      .then((data) => setEmployee(data as Employee))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load employee."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleBack = () => navigate(ROUTES.EMPLOYEES);

  const handleEdit = () => {
    if (!employee) return;
    setEditing(employee);
    setForm({
      first_name: employee.first_name,
      last_name: employee.last_name,
      email: employee.email,
      phone: employee.phone || "",
      role: employee.role || "EMPLOYEE",
      department_id: employee.department_id || "",
      designation_id: employee.designation_id || "",
      joining_date: employee.joining_date || "",
      status: employee.status || "ACTIVE",
      password: "",
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
      await updateEmployee(editing.user_id, {
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        phone: form.phone,
        role: form.role,
        department_id: form.department_id || undefined,
        designation_id: form.designation_id || undefined,
        joining_date: form.joining_date || undefined,
        status: form.status || undefined,
      });
      setModalOpen(false);
      // Refresh employee data
      if (id) {
        employeeService.getById(id).then((data) => setEmployee(data as Employee));
      }
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

  if (loading) return <Loader />;

  if (error || !employee) {
    return (
      <div>
        <PageHeader title="Employee Details" />
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error || "Employee not found."}
        </div>
        <Button onClick={handleBack} variant="ghost" className="mt-4">
          Back to Employees
        </Button>
      </div>
    );
  }

  const departmentName =
    departments.find((d) => d.department_id === employee.department_id)?.name ||
    employee.department_id ||
    "-";

  const designationName =
    designations.find((d: Designation) => d.designation_id === employee.designation_id)?.name ||
    employee.designation_id ||
    "-";

  return (
    <div>
      <PageHeader
        title="Employee Details"
        subtitle={`Viewing details for ${employee.first_name} ${employee.last_name}`}
        actions={
          canManage ? (
            <div className="flex gap-2">
              <Button onClick={handleBack} variant="ghost">
                Back
              </Button>
              <Button onClick={handleEdit}>Edit Employee</Button>
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
            <div className="flex flex-col items-center">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-slate-200 text-2xl font-bold text-slate-600">
                {employee.first_name?.[0]}{employee.last_name?.[0]}
              </div>
              <h2 className="mt-4 text-xl font-semibold text-slate-900">
                {employee.first_name} {employee.last_name}
              </h2>
              <p className="text-sm text-slate-500">{employee.email}</p>
              <StatusBadge status={employee.status} />
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="card p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">Employee Information</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Employee ID</p>
                <p className="mt-1 text-sm text-slate-900">{employee.employee_code || "-"}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Email</p>
                <p className="mt-1 text-sm text-slate-900">{employee.email}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Phone</p>
                <p className="mt-1 text-sm text-slate-900">{employee.phone || "-"}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Role</p>
                <p className="mt-1 text-sm text-slate-900">{employee.role || "-"}</p>
              </div>
            </div>
          </div>

          <div className="card mt-6 p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">Employment Information</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Department</p>
                <p className="mt-1 text-sm text-slate-900">{departmentName}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Designation</p>
                <p className="mt-1 text-sm text-slate-900">{designationName}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Joining Date</p>
                <p className="mt-1 text-sm text-slate-900">{formatDate(employee.joining_date)}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Working Duration</p>
                <p className="mt-1 text-sm text-slate-900">
                  {employee.working_duration || "-"}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Total Working Days</p>
                <p className="mt-1 text-sm text-slate-900">
                  {employee.total_working_days ?? "-"}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Status</p>
                <p className="mt-1 text-sm text-slate-900">{employee.status || "ACTIVE"}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <EmployeeFormModal
        open={modalOpen}
        editing={editing}
        departments={departments.filter((d: Department) => d.is_active)}
        designations={designations.filter((d: Designation) => d.is_active)}
        form={form}
        submitting={submitting}
        formError={formError}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        onFormChange={(field, value) => setForm({ ...form, [field]: value })}
      />
    </div>
  );
}
