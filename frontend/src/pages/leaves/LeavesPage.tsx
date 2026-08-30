/**
 * LeavesPage.
 *
 * Role-aware leave management page.
 *
 * - EMPLOYEE: self-service leave (apply, view own history).
 * - HR_MANAGER / ADMIN / SUPER_ADMIN: manage leave for all employees.
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { useLeaves } from "@/hooks/useLeaves";
import { useEmployees } from "@/hooks/useEmployees";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { formatDate } from "@/utils/helpers";
import { LeaveRecord } from "@/types/leave";
import { Employee } from "@/types/employee";
import { ROLES } from "@/utils/constants";
import { toastSuccess, toastApiError } from "@/components/common/ToastProvider";
import { leaveService } from "@/services/leave.service";
import { exportObjectsToCsv } from "@/utils/exportCsv";

const EMPTY_FORM = {
  employee_id: "",
  start_date: "",
  end_date: "",
  leave_type: "ANNUAL",
  reason: "",
};

export function LeavesPage() {
  const { user } = useAuth();
  const { leaves, total_records, total_pages, page, loading, error, list, apply, updateStatus } = useLeaves();
  const { employees, list: listEmployees } = useEmployees();

  const isEmployee = user?.role === ROLES.EMPLOYEE;
  const canManage = user?.role === ROLES.SUPER_ADMIN || user?.role === ROLES.ADMIN || user?.role === ROLES.HR_MANAGER;
  const initialLoadDone = useRef(false);

  useEffect(() => {
    if (canManage && user?._id && !initialLoadDone.current) {
      setSelectedEmployee(user._id);
      initialLoadDone.current = true;
    }
  }, [canManage, user?._id]);

  useEffect(() => {
    listEmployees({ page_size: 1000 });
  }, [listEmployees]);

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [leaveTypeFilter, setLeaveTypeFilter] = useState("");
  const [startDateFilter, setStartDateFilter] = useState("");
  const [endDateFilter, setEndDateFilter] = useState("");
  const [confirmAction, setConfirmAction] = useState<{ leave: LeaveRecord; action: "APPROVED" | "REJECTED" } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const activeEmployees = employees.filter((e) => e.is_active ?? true);

  const loadData = useCallback(
    (pageNum = 1) => {
      list({
        employee_id: isEmployee ? user?._id : (selectedEmployee || undefined),
        status: statusFilter || undefined,
        leave_type: leaveTypeFilter || undefined,
        start_date: startDateFilter || undefined,
        end_date: endDateFilter || undefined,
        page: pageNum,
        page_size: 10,
      });
    },
    [isEmployee, user?._id, selectedEmployee, statusFilter, leaveTypeFilter, startDateFilter, endDateFilter, list]
  );

  useEffect(() => {
    loadData(1);
  }, [selectedEmployee, statusFilter, leaveTypeFilter, startDateFilter, endDateFilter, isEmployee, user?._id, loadData]);

  const openCreate = () => {
    setForm({
      ...EMPTY_FORM,
      employee_id: isEmployee ? (user?._id || "") : (selectedEmployee || ""),
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      await apply({
        employee_id: isEmployee ? user?._id : form.employee_id,
        start_date: form.start_date,
        end_date: form.end_date,
        leave_type: form.leave_type,
        reason: form.reason,
      });
      setModalOpen(false);
      toastSuccess("Leave applied successfully.");
      loadData(1);
    } catch (err) {
      const message = err && typeof err === "object" && "message" in err
        ? String((err as { message: string }).message)
        : "Something went wrong.";
      setFormError(message);
      toastApiError(err, "Failed to apply leave");
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmAction = async () => {
    if (!confirmAction) return;
    setActionLoading(true);
    try {
      await updateStatus(confirmAction.leave.leave_id, confirmAction.action);
      toastSuccess(`Leave ${confirmAction.action.toLowerCase()} successfully.`);
      setConfirmAction(null);
      loadData(page);
    } catch (err) {
      toastApiError(err, `Failed to ${confirmAction.action.toLowerCase()} leave`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const res = await leaveService.list({
        employee_id: isEmployee ? user?._id : (selectedEmployee || undefined),
        status: statusFilter || undefined,
        leave_type: leaveTypeFilter || undefined,
        start_date: startDateFilter || undefined,
        end_date: endDateFilter || undefined,
        page: 1,
        page_size: 1000,
      });
      exportObjectsToCsv(
        "leaves.csv",
        res.leaves,
        [
          { header: "Employee Name", key: "employee_name" },
          { header: "Employee Code", key: "employee_code" },
          { header: "Leave Type", key: "leave_type" },
          { header: "Start Date", key: "start_date" },
          { header: "End Date", key: "end_date" },
          { header: "Reason", key: "reason" },
          { header: "Status", key: "status" },
          { header: "Applied Date", key: "created_at" },
        ]
      );
      toastSuccess("Leave data exported successfully.");
    } catch (err) {
      toastApiError(err, "Failed to export leaves");
    }
  };

  const handleClearFilters = () => {
    if (canManage && user?._id) {
      setSelectedEmployee(user._id);
    } else {
      setSelectedEmployee("");
    }
    setStatusFilter("");
    setLeaveTypeFilter("");
    setStartDateFilter("");
    setEndDateFilter("");
  };

  return (
    <div>
      <PageHeader
        title={isEmployee ? "My Leaves" : "Leave Management"}
        subtitle={
          isEmployee
            ? "View and manage your leave requests."
            : "Review and manage employee leave requests."
        }
        actions={
          <div className="flex gap-2">
            <Button variant="ghost" onClick={handleExport}>Export CSV</Button>
            <Button onClick={openCreate}>Apply Leave</Button>
          </div>
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      {canManage && (
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end">
          <div>
            <label className="label">Employee</label>
            <select
              value={selectedEmployee}
              onChange={(e) => setSelectedEmployee(e.target.value)}
              className="input"
            >
              <option value="">All Employees</option>
              {activeEmployees.map((emp: Employee) => (
                <option key={emp.user_id} value={emp.user_id}>
                  {emp.first_name} {emp.last_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
          <div>
            <label className="label">Leave Type</label>
            <select
              value={leaveTypeFilter}
              onChange={(e) => setLeaveTypeFilter(e.target.value)}
              className="input"
            >
              <option value="">All Types</option>
              <option value="ANNUAL">Annual</option>
              <option value="SICK">Sick</option>
              <option value="CASUAL">Casual</option>
              <option value="UNPAID">Unpaid</option>
            </select>
          </div>
          <Input
            label="Start Date"
            name="start_date"
            type="date"
            value={startDateFilter}
            onChange={(e) => setStartDateFilter(e.target.value)}
          />
          <Input
            label="End Date"
            name="end_date"
            type="date"
            value={endDateFilter}
            onChange={(e) => setEndDateFilter(e.target.value)}
          />
          <button
            onClick={() => loadData(1)}
            className="btn-primary rounded-lg px-4 py-2 text-sm font-medium"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium"
          >
            Clear
          </button>
        </div>
      )}

      {isEmployee && (
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end">
          <div>
            <label className="label">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
          <Input
            label="Start Date"
            name="start_date"
            type="date"
            value={startDateFilter}
            onChange={(e) => setStartDateFilter(e.target.value)}
          />
          <Input
            label="End Date"
            name="end_date"
            type="date"
            value={endDateFilter}
            onChange={(e) => setEndDateFilter(e.target.value)}
          />
          <button
            onClick={() => loadData(1)}
            className="btn-primary rounded-lg px-4 py-2 text-sm font-medium"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium"
          >
            Clear
          </button>
        </div>
      )}

      {loading && leaves.length === 0 ? (
        <Loader />
      ) : leaves.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No leave records found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                {!isEmployee && (
                  <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>
                )}
                <th className="px-4 py-3 text-left font-medium text-slate-500">Type</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Start Date</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">End Date</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                {canManage && (
                  <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {leaves.map((leave) => (
                <tr key={leave.leave_id} className="hover:bg-slate-50">
                  {!isEmployee && (
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {leave.employee_name || employees.find((e: Employee) => e.user_id === leave.employee_id)?.first_name || leave.employee_id}
                    </td>
                  )}
                  <td className="px-4 py-3 text-slate-600">{leave.leave_type}</td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(leave.start_date)}</td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(leave.end_date)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={leave.status} />
                  </td>
                  {canManage && (
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        {leave.status === "PENDING" && (
                          <>
                            <button
                              onClick={() => setConfirmAction({ leave, action: "APPROVED" })}
                              className="rounded border border-green-200 px-2 py-1 text-xs font-medium text-green-600 hover:bg-green-50"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => setConfirmAction({ leave, action: "REJECTED" })}
                              className="rounded border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                            >
                              Reject
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={total_pages}
          totalRecords={total_records}
          onPageChange={(nextPage) => loadData(nextPage)}
        />
      )}

      <Modal
        open={modalOpen}
        title="Apply for leave"
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError ? (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
          ) : null}

          {canManage && (
            <div>
              <label className="label" htmlFor="employee_id">
                Employee
              </label>
              <select
                id="employee_id"
                name="employee_id"
                value={form.employee_id}
                onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                className="input"
                required
              >
                <option value="">Select employee</option>
                {activeEmployees.map((emp: Employee) => (
                  <option key={emp.user_id} value={emp.user_id}>
                    {emp.first_name} {emp.last_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Start Date"
              name="start_date"
              type="date"
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
              required
            />
            <Input
              label="End Date"
              name="end_date"
              type="date"
              value={form.end_date}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="label" htmlFor="leave_type">
              Leave Type
            </label>
            <select
              id="leave_type"
              name="leave_type"
              value={form.leave_type}
              onChange={(e) => setForm({ ...form, leave_type: e.target.value })}
              className="input"
            >
              <option value="ANNUAL">Annual</option>
              <option value="SICK">Sick</option>
              <option value="CASUAL">Casual</option>
              <option value="UNPAID">Unpaid</option>
            </select>
          </div>

          <Input
            label="Reason (optional)"
            name="reason"
            value={form.reason}
            onChange={(e) => setForm({ ...form, reason: e.target.value })}
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
              Apply leave
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        open={confirmAction !== null}
        title={confirmAction?.action === "APPROVED" ? "Approve leave" : "Reject leave"}
        onClose={() => setConfirmAction(null)}
      >
        <p className="text-sm text-slate-600">
          {confirmAction?.action === "APPROVED"
            ? `Approve leave request for ${confirmAction?.leave.employee_name || "employee"}?`
            : `Reject leave request for ${confirmAction?.leave.employee_name || "employee"}?`}
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setConfirmAction(null)}>
            Cancel
          </Button>
          <Button
            variant={confirmAction?.action === "APPROVED" ? "primary" : "danger"}
            loading={actionLoading}
            onClick={handleConfirmAction}
          >
            {confirmAction?.action === "APPROVED" ? "Approve" : "Reject"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
