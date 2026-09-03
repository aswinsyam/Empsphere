/**
 * EmployeesPage.
 *
 * Main Employee Management page. Lists employees with search/filters and
 * lets privileged users view, create, edit, and activate/deactivate employees.
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { cn, formatDate } from "@/utils/helpers";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { Employee } from "@/types/employee";
import { Department } from "@/types/department";
import { Designation } from "@/types/designation";
import { EmployeeFormModal } from "@/components/employees/EmployeeFormModal";
import { canManageEmployees, ROUTES } from "@/utils/constants";
import { employeeService } from "@/services/employee.service";
import { departmentService } from "@/services/department.service";
import { designationService } from "@/services/designation.service";

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

export function EmployeesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [pageSize] = useState(10);

  const canManage = canManageEmployees(user?.role);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Employee | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterDepartment, setFilterDepartment] = useState("");
  const [joiningDateFrom, setJoiningDateFrom] = useState("");
  const [joiningDateTo, setJoiningDateTo] = useState("");

  useEffect(() => {
    departmentService.list({ include_inactive: true }).then((r) => setDepartments(r.departments));
    designationService.list({ include_inactive: true }).then((r) => setDesignations(r.designations));
  }, []);

  const loadEmployees = async (pageNum = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result = await employeeService.list({
        search: search || undefined,
        status: filterStatus || undefined,
        department_id: filterDepartment || undefined,
        joining_date_from: joiningDateFrom || undefined,
        joining_date_to: joiningDateTo || undefined,
        page: pageNum,
        page_size: pageSize,
      });
      setEmployees(result.employees);
      setPage(result.page);
      setTotalPages(result.total_pages);
      setTotalRecords(result.total_records);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load employees");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees(1);
  }, [search, filterStatus, filterDepartment, joiningDateFrom, joiningDateTo]);

  const resetFilters = () => {
    setSearch("");
    setFilterStatus("");
    setFilterDepartment("");
    setJoiningDateFrom("");
    setJoiningDateTo("");
  };

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditing(emp);
    setForm({
      first_name: emp.first_name,
      last_name: emp.last_name,
      email: emp.email,
      phone: emp.phone || "",
      role: emp.role || "EMPLOYEE",
      department_id: emp.department_id || "",
      designation_id: emp.designation_id || "",
      joining_date: emp.joining_date || "",
      status: emp.status || "ACTIVE",
      password: "",
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
        await employeeService.update(editing.user_id, {
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
      } else {
        await employeeService.create({
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          password: form.password,
          phone: form.phone,
          role: form.role,
          department_id: form.department_id || undefined,
          designation_id: form.designation_id || undefined,
          joining_date: form.joining_date || undefined,
          status: form.status || undefined,
        });
      }
      setModalOpen(false);
      await loadEmployees(1);
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

  const handleStatusToggle = async (emp: Employee) => {
    const newStatus = emp.status === "ACTIVE" ? "INACTIVE" : "ACTIVE";
    const confirmMessage = newStatus === "INACTIVE"
      ? `Deactivate employee "${emp.first_name} ${emp.last_name}"? This employee will no longer be able to log in.`
      : `Activate employee "${emp.first_name} ${emp.last_name}"?`;
    if (!window.confirm(confirmMessage)) return;
    try {
      await employeeService.update(emp.user_id, { status: newStatus });
      await loadEmployees(1);
    } catch {
      // error handled silently
    }
  };

  const handleViewEmployee = (emp: Employee) => {
    navigate(`${ROUTES.EMPLOYEES}/${emp.user_id}`);
  };

  return (
    <div>
      <PageHeader
        title="Employees"
        subtitle="Manage employees in your organization."
        actions={
          canManage ? (
            <Button onClick={openCreate}>Create Employee</Button>
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
          placeholder="Search by name, email, code..."
          className="sm:max-w-xs"
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="input"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
        <select
          value={filterDepartment}
          onChange={(e) => setFilterDepartment(e.target.value)}
          className="input"
        >
          <option value="">All Departments</option>
          {departments.map((dept) => (
            <option key={dept.department_id} value={dept.department_id}>
              {dept.name}
            </option>
          ))}
        </select>
        <Input
          label="Joining Date From"
          name="joining_date_from"
          type="date"
          value={joiningDateFrom}
          onChange={(e) => setJoiningDateFrom(e.target.value)}
          className="sm:max-w-xs"
        />
        <Input
          label="Joining Date To"
          name="joining_date_to"
          type="date"
          value={joiningDateTo}
          onChange={(e) => setJoiningDateTo(e.target.value)}
          className="sm:max-w-xs"
        />
        <button
          onClick={resetFilters}
          className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium"
        >
          Clear Filters
        </button>
      </div>

      {loading && employees.length === 0 ? (
        <Loader />
      ) : employees.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No employees found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Employee ID</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Email</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Phone</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Department</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Joining Date</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                {canManage ? (
                  <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {employees.map((emp) => (
                <tr key={emp.user_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{emp.employee_code || "-"}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    <button
                      onClick={() => handleViewEmployee(emp)}
                      className="text-left hover:underline"
                    >
                      {emp.first_name} {emp.last_name}
                    </button>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{emp.email}</td>
                  <td className="px-4 py-3 text-slate-600">{emp.phone || "-"}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {departments.find((d) => d.department_id === emp.department_id)?.name || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(emp.joining_date)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={emp.status || "ACTIVE"} />
                  </td>
                  {canManage ? (
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleViewEmployee(emp)}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        >
                          View
                        </button>
                        <button
                          onClick={() => openEdit(emp)}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleStatusToggle(emp)}
                          className={cn(
                            "rounded border px-2 py-1 text-xs font-medium",
                            emp.status === "ACTIVE"
                              ? "border-amber-200 text-amber-700 hover:bg-amber-50"
                              : "border-green-200 text-green-600 hover:bg-green-50"
                          )}
                        >
                          {emp.status === "ACTIVE" ? "Deactivate" : "Activate"}
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
          onPageChange={(nextPage) => loadEmployees(nextPage)}
        />
      )}

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
