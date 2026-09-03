/**
 * AttendancePage.
 *
 * Role-aware attendance management page.
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { useAuth } from "@/hooks/useAuth";
import { attendanceService } from "@/services/attendance.service";
import { employeeService } from "@/services/employee.service";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import {
  AttendanceFormModal,
  AttendanceFormValues,
} from "@/components/attendance/AttendanceFormModal";
import { formatDate } from "@/utils/helpers";
import { Employee } from "@/types/employee";
import { ROLES } from "@/utils/constants";
import { toastApiError, toastSuccess } from "@/components/common/ToastProvider";

const EMPTY_FORM: AttendanceFormValues = {
  date: new Date().toISOString().split("T")[0],
  status: "PRESENT",
  check_in: "",
  check_out: "",
  remarks: "",
};

/** Convert an ISO datetime (or "YYYY-MM-DDTHH:MM:SS") into "HH:MM". */
function toTimeInput(value?: string | null): string {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

/** Convert "YYYY-MM-DD" + "HH:MM" into an ISO datetime string for the API. */
function toIsoFromForm(date: string, time: string): string | undefined {
  if (!date || !time) return undefined;
  return `${date}T${time}:00`;
}

export function AttendancePage() {
  const { user } = useAuth();

  const [records, setRecords] = useState<any[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);

  const isEmployee = user?.role === ROLES.EMPLOYEE;
  const canManage = user?.role === ROLES.SUPER_ADMIN || user?.role === ROLES.ADMIN || user?.role === ROLES.HR_MANAGER;
  const showMyAttendance = isEmployee || canManage;

  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [editingAttendanceId, setEditingAttendanceId] = useState<string | null>(null);
  const [form, setForm] = useState<AttendanceFormValues>({ ...EMPTY_FORM });
  const initialLoadDone = useRef(false);

  useEffect(() => {
    if (canManage && user?._id && !initialLoadDone.current) {
      setSelectedEmployee(user._id);
      initialLoadDone.current = true;
    }
  }, [canManage, user?._id]);

  const activeEmployees = employees.filter((e) => e.is_active ?? true);

  const loadData = useCallback(
    (pageNum = 1) => {
      setLoading(true);
      setError(null);
      attendanceService.list({
        employee_id: isEmployee ? user?._id : (selectedEmployee || undefined),
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        status: filterStatus || undefined,
        page: pageNum,
        page_size: 10,
      }).then((result) => {
        setRecords(result.attendance);
        setPage(result.page);
        setTotalPages(result.total_pages);
        setTotalRecords(result.total_records);
        setLoading(false);
      }).catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load attendance");
        setLoading(false);
      });
    },
    [isEmployee, user?._id, selectedEmployee, startDate, endDate, filterStatus]
  );

  useEffect(() => {
    employeeService.list({ page_size: 1000 }).then((r) => setEmployees(r.employees));
  }, []);

  useEffect(() => {
    loadData(1);
  }, [selectedEmployee, startDate, endDate, isEmployee, user?._id, loadData]);

  useEffect(() => {
    const empId = (isEmployee || canManage) ? user?._id : (selectedEmployee || (records[0]?.employee_id));
    if (empId) {
      attendanceService.summary(empId).then(setSummary).catch(() => {});
    }
  }, [showMyAttendance, user?._id, selectedEmployee, records, isEmployee, canManage]);

  const getTodayRecord = () => {
    if (!user?._id) return null;
    const today = new Date().toISOString().split("T")[0];
    return records.find((r) => r.date === today && r.employee_id === user._id) || null;
  };

  const todayRecord = getTodayRecord();
  const hasCheckedIn = Boolean(todayRecord?.check_in);
  const hasCheckedOut = Boolean(todayRecord?.check_out);
  const canCheckIn = (isEmployee || canManage) && !hasCheckedIn;
  const canCheckOut = (isEmployee || canManage) && hasCheckedIn && !hasCheckedOut;

  const handleCheckIn = async () => {
    setActionError(null);
    setSubmitting(true);
    try {
      await attendanceService.checkIn();
      toastSuccess("Checked in successfully.");
      loadData(1);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to check in.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCheckOut = async () => {
    setActionError(null);
    setSubmitting(true);
    try {
      await attendanceService.checkOut();
      toastSuccess("Checked out successfully.");
      loadData(1);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to check out.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleFilter = () => {
    loadData(1);
  };

  const handleClearFilters = () => {
    if (canManage && user?._id) {
      setSelectedEmployee(user._id);
    } else {
      setSelectedEmployee("");
    }
    setStartDate("");
    setEndDate("");
    setFilterStatus("");
  };

  const openCreateModal = () => {
    setActionError(null);
    setModalMode("create");
    setEditingAttendanceId(null);
    setForm({
      ...EMPTY_FORM,
      date: new Date().toISOString().split("T")[0],
    });
    setModalOpen(true);
  };

  const openEditModal = (record: any) => {
    setActionError(null);
    setModalMode("edit");
    setEditingAttendanceId(record.attendance_id);
    setSelectedEmployee(record.employee_id);
    setForm({
      date: record.date || "",
      status: record.status || "PRESENT",
      check_in: toTimeInput(record.check_in),
      check_out: toTimeInput(record.check_out),
      remarks: record.remarks || "",
    });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingAttendanceId(null);
    setActionError(null);
  };

  const handleSubmitModal = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);

    if (!selectedEmployee) {
      setActionError("Select an employee before saving attendance.");
      return;
    }
    if (!form.date) {
      setActionError("Date is required.");
      return;
    }
    if (form.check_in && form.check_out && form.check_in >= form.check_out) {
      setActionError("Check-out time must be after check-in time.");
      return;
    }

    const checkInIso = toIsoFromForm(form.date, form.check_in);
    const checkOutIso = toIsoFromForm(form.date, form.check_out);

    setSubmitting(true);
    try {
      if (modalMode === "edit" && editingAttendanceId) {
        // Existing record: use PUT to update
        await attendanceService.update(editingAttendanceId, {
          status: form.status,
          check_in: checkInIso,
          check_out: checkOutIso,
          remarks: form.remarks || undefined,
        });
        toastSuccess("Attendance updated successfully.");
      } else {
        // New record (or upsert by manager) — POST /attendance/ handles both
        await attendanceService.mark({
          employee_id: selectedEmployee,
          date: form.date,
          status: form.status,
          check_in: checkInIso,
          check_out: checkOutIso,
          remarks: form.remarks || undefined,
        });
        toastSuccess("Attendance saved successfully.");
      }
      closeModal();
      loadData(1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setActionError(msg);
      toastApiError(err, "Failed to save attendance");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title={isEmployee ? "My Attendance" : "Attendance"}
        subtitle={
          isEmployee
            ? "Track your own attendance."
            : "Track and manage employee attendance."
        }
        actions={
          !isEmployee ? (
            <Button onClick={openCreateModal}>Mark Attendance</Button>
          ) : undefined
        }
      />

      {(error || actionError) && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">{error || actionError}</div>
      )}

      {(isEmployee || canManage) && (
        <div className="mb-6 card p-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Today&apos;s Attendance</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Date</p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {new Date().toLocaleDateString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Check In</p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {todayRecord?.check_in ? new Date(todayRecord.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Check Out</p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {todayRecord?.check_out ? new Date(todayRecord.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            {canCheckIn && (
              <Button onClick={handleCheckIn} loading={submitting}>Check In</Button>
            )}
            {canCheckOut && (
              <Button onClick={handleCheckOut} loading={submitting} variant="ghost">Check Out</Button>
            )}
            {!canCheckIn && !canCheckOut && (
              <span className="text-sm text-slate-500">
                {hasCheckedOut ? "You have completed attendance for today." : "Attendance in progress..."}
              </span>
            )}
          </div>
        </div>
      )}

      {!isEmployee && (
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
              <option value="PRESENT">Present</option>
              <option value="ABSENT">Absent</option>
              <option value="HALF_DAY">Half Day</option>
              <option value="LEAVE">Leave</option>
            </select>
          </div>
          <button
            onClick={handleFilter}
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

      {summary && (isEmployee || canManage) && (
        <div className="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-5">
          <div className="card p-4 text-center">
            <p className="text-xs uppercase tracking-wide text-slate-400">Total Days</p>
            <p className="text-xl font-semibold text-slate-900">{summary.total_days}</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-xs uppercase tracking-wide text-slate-400">Present</p>
            <p className="text-xl font-semibold text-green-600">{summary.present_days}</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-xs uppercase tracking-wide text-slate-400">Absent</p>
            <p className="text-xl font-semibold text-red-600">{summary.absent_days}</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-xs uppercase tracking-wide text-slate-400">Half Days</p>
            <p className="text-xl font-semibold text-amber-600">{summary.half_days}</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-xs uppercase tracking-wide text-slate-400">Attendance %</p>
            <p className="text-xl font-semibold text-brand-600">{summary.attendance_percentage}%</p>
          </div>
        </div>
      )}

      {loading && records.length === 0 ? (
        <Loader />
      ) : records.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No attendance records found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Date</th>
                {!isEmployee && (
                  <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>
                )}
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Check In</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Check Out</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Remarks</th>
                {canManage && (
                  <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((record) => (
                <tr key={record.attendance_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{formatDate(record.date)}</td>
                  {!isEmployee && (
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {employees.find((e: Employee) => e.user_id === record.employee_id)?.first_name || record.employee_id}
                    </td>
                  )}
                  <td className="px-4 py-3">
                    <StatusBadge status={record.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">{record.check_in ? new Date(record.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{record.check_out ? new Date(record.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{record.remarks || "—"}</td>
                  {canManage && (
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEditModal(record)}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        >
                          Edit
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
          onPageChange={(nextPage) => loadData(nextPage)}
        />
      )}

      <AttendanceFormModal
        open={modalOpen}
        submitting={submitting}
        formError={actionError}
        employees={activeEmployees}
        selectedEmployee={selectedEmployee}
        form={form}
        mode={modalMode}
        onClose={closeModal}
        onSubmit={handleSubmitModal}
        onFormChange={(field, value) => setForm({ ...form, [field]: value })}
        onEmployeeChange={(value) => setSelectedEmployee(value)}
      />
    </div>
  );
}