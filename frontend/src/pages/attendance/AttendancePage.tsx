/**
 * AttendancePage.
 *
 * Role-aware attendance management page.
 *
 * - EMPLOYEE: simple check-in/check-out + own history.
 * - HR_MANAGER / ADMIN / SUPER_ADMIN: manage attendance for all employees.
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { useAttendance } from "@/hooks/useAttendance";
import { useEmployees } from "@/hooks/useEmployees";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { AttendanceFormModal } from "@/components/attendance/AttendanceFormModal";
import { formatDate } from "@/utils/helpers";
import { Employee } from "@/types/employee";
import { ROLES } from "@/utils/constants";

export function AttendancePage() {
  const {
    records,
    summary,
    loading,
    error,
    page,
    total_records,
    total_pages,
    list,
    mark,
    update,
    loadSummary,
    checkIn,
    checkOut,
  } = useAttendance();
  const { user } = useAuth();
  const { employees, list: listEmployees } = useEmployees();

  const isEmployee = user?.role === ROLES.EMPLOYEE;
  const canManage = user?.role === ROLES.SUPER_ADMIN || user?.role === ROLES.ADMIN || user?.role === ROLES.HR_MANAGER;
  const showMyAttendance = isEmployee || canManage;

  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [markModalOpen, setMarkModalOpen] = useState(false);
  const [markForm, setMarkForm] = useState({
    date: new Date().toISOString().split("T")[0],
    status: "PRESENT",
    check_in: "",
    check_out: "",
    remarks: "",
  });
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
      list({
        employee_id: isEmployee ? user?._id : (selectedEmployee || undefined),
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        status: filterStatus || undefined,
        page: pageNum,
        page_size: 10,
      });
    },
    [isEmployee, user?._id, selectedEmployee, startDate, endDate, filterStatus, list]
  );

  useEffect(() => {
    listEmployees({ page_size: 1000 });
  }, [listEmployees]);

  useEffect(() => {
    loadData(1);
  }, [selectedEmployee, startDate, endDate, isEmployee, user?._id, loadData]);

  useEffect(() => {
    if (showMyAttendance && user?._id) {
      loadSummary({ employee_id: user._id });
    } else if (!showMyAttendance && selectedEmployee) {
      loadSummary({ employee_id: selectedEmployee });
    } else if (!showMyAttendance && !selectedEmployee && records.length > 0) {
      const firstEmp = records[0]?.employee_id;
      if (firstEmp) {
        loadSummary({ employee_id: firstEmp });
      }
    }
  }, [showMyAttendance, user?._id, selectedEmployee, records, loadSummary]);

  const getTodayRecord = () => {
    if (!user?._id) return null;
    const today = new Date().toISOString().split("T")[0];
    return records.find((r) => r.date === today && r.employee_id === user._id) || null;
  };

  const todayRecord = getTodayRecord();
  const hasCheckedIn = Boolean(todayRecord?.check_in);
  const hasCheckedOut = Boolean(todayRecord?.check_out);
  const canCheckIn = showMyAttendance && !hasCheckedIn;
  const canCheckOut = showMyAttendance && hasCheckedIn && !hasCheckedOut;

  const handleCheckIn = async () => {
    setActionError(null);
    setActionSuccess(null);
    setSubmitting(true);
    try {
      await checkIn();
      setActionSuccess("Checked in successfully.");
      loadData(1);
    } catch (err) {
      setActionError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Failed to check in."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleCheckOut = async () => {
    setActionError(null);
    setActionSuccess(null);
    setSubmitting(true);
    try {
      await checkOut();
      setActionSuccess("Checked out successfully.");
      loadData(1);
    } catch (err) {
      setActionError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Failed to check out."
      );
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

  const handleMark = async (payload: { employee_id?: string; date: string; status?: string; check_in?: string; check_out?: string; remarks?: string }) => {
    setSubmitting(true);
    try {
      await mark(payload);
      setActionSuccess("Attendance marked successfully.");
      setMarkModalOpen(false);
      loadData(1);
    } catch (err) {
      setActionError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Something went wrong."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (id: string, payload: { status?: string; check_in?: string; check_out?: string; remarks?: string }) => {
    setSubmitting(true);
    try {
      await update(id, payload);
      loadData(1);
    } catch (err) {
      setActionError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Something went wrong."
      );
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
            <Button onClick={() => setMarkModalOpen(true)}>Mark Attendance</Button>
          ) : undefined
        }
      />

      {(error || actionError) && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">{error || actionError}</div>
      )}
      {actionSuccess && (
        <div className="mb-4 rounded-lg bg-green-50 p-4 text-sm text-green-700">{actionSuccess}</div>
      )}

      {showMyAttendance && (
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

      {summary && showMyAttendance && (
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
                          onClick={() => handleUpdate(record.attendance_id, {
                            status: record.status,
                            check_in: record.check_in,
                            check_out: record.check_out,
                            remarks: record.remarks,
                          })}
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

      {total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={total_pages}
          totalRecords={total_records}
          onPageChange={(nextPage) => loadData(nextPage)}
        />
      )}

      <AttendanceFormModal
        open={markModalOpen}
        submitting={submitting}
        formError={actionError}
        employees={activeEmployees}
        selectedEmployee={selectedEmployee}
        form={markForm}
        onClose={() => setMarkModalOpen(false)}
        onSubmit={(e) => {
          e.preventDefault();
          if (!selectedEmployee) {
            setActionError("Select an employee before marking attendance.");
            return;
          }
          const checkInTime = markForm.check_in ? `${markForm.date}T${markForm.check_in}:00` : undefined;
          const checkOutTime = markForm.check_out ? `${markForm.date}T${markForm.check_out}:00` : undefined;
          handleMark({
            employee_id: selectedEmployee,
            date: markForm.date,
            status: markForm.status,
            check_in: checkInTime,
            check_out: checkOutTime,
            remarks: markForm.remarks || undefined,
          });
        }}
        onFormChange={(field, value) => setMarkForm({ ...markForm, [field]: value })}
        onEmployeeChange={(value) => setSelectedEmployee(value)}
      />
    </div>
  );
}
