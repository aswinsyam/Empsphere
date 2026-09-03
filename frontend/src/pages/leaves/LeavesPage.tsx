/**
 * LeavesPage.
 *
 * Leave management page — employees apply for leave; managers approve/reject.
 */

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { leaveService } from "@/services/leave.service";
import { employeeService } from "@/services/employee.service";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { Modal } from "@/components/common/Modal";
import { Employee } from "@/types/employee";
import { ROLES } from "@/utils/constants";
import { toastSuccess, toastApiError } from "@/components/common/ToastProvider";

export function LeavesPage() {
  const { user } = useAuth();

  const [leaves, setLeaves] = useState<any[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [pageSize] = useState(10);

  const isEmployee = user?.role === ROLES.EMPLOYEE;
  const canManage = user?.role === ROLES.SUPER_ADMIN || user?.role === ROLES.ADMIN || user?.role === ROLES.HR_MANAGER;

  const [filterStatus, setFilterStatus] = useState("");
  const [filterLeaveType, setFilterLeaveType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    employee_id: "",
    start_date: "",
    end_date: "",
    leave_type: "ANNUAL",
    reason: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Decision (Approve/Reject) modal state
  const [decisionModalOpen, setDecisionModalOpen] = useState(false);
  const [decisionType, setDecisionType] = useState<"APPROVED" | "REJECTED">("APPROVED");
  const [decisionTarget, setDecisionTarget] = useState<any | null>(null);
  const [decisionReason, setDecisionReason] = useState("");
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [decisionSubmitting, setDecisionSubmitting] = useState(false);

  const loadLeaves = async (pageNum = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result = await leaveService.list({
        employee_id: isEmployee ? user?._id : (selectedEmployee || undefined),
        status: filterStatus || undefined,
        leave_type: filterLeaveType || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        page: pageNum,
        page_size: pageSize,
      });
      setLeaves(result.leaves);
      setPage(result.page);
      setTotalPages(result.total_pages);
      setTotalRecords(result.total_records);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load leaves");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (canManage) {
      employeeService.list({ page_size: 1000 }).then((r) => setEmployees(r.employees));
    }
  }, [canManage]);

  useEffect(() => {
    loadLeaves(1);
  }, [selectedEmployee, filterStatus, filterLeaveType, startDate, endDate, isEmployee]);

  const openApply = () => {
    setForm({
      employee_id: isEmployee ? (user?._id || "") : "",
      start_date: "",
      end_date: "",
      leave_type: "ANNUAL",
      reason: "",
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      await leaveService.apply({
        employee_id: form.employee_id || user?._id || "",
        start_date: form.start_date,
        end_date: form.end_date,
        leave_type: form.leave_type,
        reason: form.reason || undefined,
      });
      toastSuccess("Leave applied successfully.");
      setModalOpen(false);
      await loadLeaves(1);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  const openDecisionModal = (leave: any, type: "APPROVED" | "REJECTED") => {
    setDecisionTarget(leave);
    setDecisionType(type);
    setDecisionReason("");
    setDecisionError(null);
    setDecisionModalOpen(true);
  };

  const closeDecisionModal = () => {
    setDecisionModalOpen(false);
    setDecisionTarget(null);
    setDecisionReason("");
    setDecisionError(null);
  };

  const submitDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!decisionTarget) return;
    if (!decisionReason.trim()) {
      setDecisionError(
        decisionType === "APPROVED"
          ? "Approval reason is required."
          : "Rejection reason is required."
      );
      return;
    }
    setDecisionError(null);
    setDecisionSubmitting(true);
    try {
      await leaveService.updateStatus(decisionTarget.leave_id, decisionType, decisionReason.trim());
      toastSuccess(`Leave ${decisionType.toLowerCase()} successfully.`);
      closeDecisionModal();
      await loadLeaves(1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setDecisionError(msg);
      toastApiError(err, `Failed to ${decisionType.toLowerCase()} leave`);
    } finally {
      setDecisionSubmitting(false);
    }
  };

  const clearFilters = () => {
    setFilterStatus("");
    setFilterLeaveType("");
    setStartDate("");
    setEndDate("");
    setSelectedEmployee("");
  };

  return (
    <div>
      <PageHeader
        title="Leaves"
        subtitle="Manage leave requests."
        actions={
          <Button onClick={openApply}>Apply for Leave</Button>
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
              {employees.map((emp: Employee) => (
                <option key={emp.user_id} value={emp.user_id}>
                  {emp.first_name} {emp.last_name}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Start Date"
            name="start_date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <Input
            label="End Date"
            name="end_date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <div>
            <label className="label">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
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
              value={filterLeaveType}
              onChange={(e) => setFilterLeaveType(e.target.value)}
              className="input"
            >
              <option value="">All Types</option>
              <option value="ANNUAL">Annual</option>
              <option value="SICK">Sick</option>
              <option value="CASUAL">Casual</option>
              <option value="UNPAID">Unpaid</option>
            </select>
          </div>
          <button
            onClick={() => loadLeaves(1)}
            className="btn-primary rounded-lg px-4 py-2 text-sm font-medium"
          >
            Apply Filters
          </button>
          <button
            onClick={clearFilters}
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
                {canManage && <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>}
                <th className="px-4 py-3 text-left font-medium text-slate-500">Dates</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Type</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Reason</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Decision Note</th>
                {canManage && <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {leaves.map((leave) => (
                <tr key={leave.leave_id} className="hover:bg-slate-50">
                  {canManage && (
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {leave.employee_name || leave.employee_id}
                    </td>
                  )}
                  <td className="px-4 py-3 text-slate-600">
                    {leave.start_date} → {leave.end_date}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{leave.leave_type}</td>
                  <td className="px-4 py-3 text-slate-600">{leave.reason || "—"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={leave.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {leave.status === "APPROVED" && (leave.approval_reason || "—")}
                    {leave.status === "REJECTED" && (leave.rejection_reason || "—")}
                    {leave.status === "PENDING" && "—"}
                  </td>
                  {canManage && leave.status === "PENDING" && (
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openDecisionModal(leave, "APPROVED")}
                          className="rounded border border-green-300 px-2 py-1 text-xs font-medium text-green-700 hover:bg-green-50"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => openDecisionModal(leave, "REJECTED")}
                          className="rounded border border-red-300 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-50"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  )}
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
          onPageChange={(nextPage) => loadLeaves(nextPage)}
        />
      )}

      {modalOpen && (
        <Modal
          open={modalOpen}
          title="Apply for Leave"
          onClose={() => setModalOpen(false)}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            {formError ? (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
            ) : null}
            {!isEmployee && (
              <div>
                <label className="label">Employee</label>
                <select
                  value={form.employee_id}
                  onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">Select employee</option>
                  {employees.map((emp: Employee) => (
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
              <label className="label">Leave Type</label>
              <select
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
              <Button type="button" variant="ghost" onClick={() => setModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={submitting}>
                Apply
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {decisionModalOpen && decisionTarget && (
        <Modal
          open={decisionModalOpen}
          title={decisionType === "APPROVED" ? "Approve Leave" : "Reject Leave"}
          onClose={closeDecisionModal}
        >
          <form onSubmit={submitDecision} className="space-y-4">
            {decisionError ? (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{decisionError}</div>
            ) : null}

            <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
              <p>
                <strong>Employee:</strong> {decisionTarget.employee_name || decisionTarget.employee_id}
              </p>
              <p>
                <strong>Dates:</strong> {decisionTarget.start_date} → {decisionTarget.end_date}
              </p>
              <p>
                <strong>Type:</strong> {decisionTarget.leave_type}
              </p>
              {decisionTarget.reason ? (
                <p>
                  <strong>Applicant Reason:</strong> {decisionTarget.reason}
                </p>
              ) : null}
            </div>

            <div>
              <label className="label" htmlFor="decision_reason">
                {decisionType === "APPROVED" ? "Approval reason" : "Rejection reason"}
              </label>
              <textarea
                id="decision_reason"
                name="decision_reason"
                rows={4}
                value={decisionReason}
                onChange={(e) => setDecisionReason(e.target.value)}
                className="input"
                required
                placeholder={
                  decisionType === "APPROVED"
                    ? "e.g. Approved as per policy. Enjoy your leave!"
                    : "e.g. Insufficient leave balance for the requested period."
                }
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="ghost" onClick={closeDecisionModal}>
                Cancel
              </Button>
              <Button
                type="submit"
                loading={decisionSubmitting}
                variant={decisionType === "APPROVED" ? "primary" : "danger"}
              >
                {decisionType === "APPROVED" ? "Approve Leave" : "Reject Leave"}
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}