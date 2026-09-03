/**
 * ReportsPage.
 *
 * Centralized reporting page for management users.
 * Supports Employee, Attendance, Leave, Department, Designation, and Activity reports.
 */

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { reportService } from "@/services/report.service";
import { getErrorMessage } from "@/utils/helpers";
import { ReportResponse } from "@/types/report";
import { exportObjectsToCsv } from "@/utils/exportCsv";
import { toastSuccess } from "@/components/common/ToastProvider";

const REPORT_TYPES = [
  { value: "employees", label: "Employee Report" },
  { value: "attendance", label: "Attendance Report" },
  { value: "leaves", label: "Leave Report" },
  { value: "departments", label: "Department Report" },
  { value: "designations", label: "Designation Report" },
  { value: "activity", label: "Activity Report" },
] as const;

type ReportType = (typeof REPORT_TYPES)[number]["value"];

export function ReportsPage() {
  const [reportType, setReportType] = useState<ReportType>("employees");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ReportResponse | null>(null);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [designationId, setDesignationId] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [leaveType, setLeaveType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [joiningDateFrom, setJoiningDateFrom] = useState("");
  const [joiningDateTo, setJoiningDateTo] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [module, setModule] = useState("");
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      let result: ReportResponse;
      const params: Record<string, unknown> = {
        page,
        page_size: pageSize,
      };
      if (search) params.search = search;
      if (status) params.status = status;
      if (departmentId) params.department_id = departmentId;
      if (designationId) params.designation_id = designationId;
      if (employeeId) params.employee_id = employeeId;
      if (leaveType) params.leave_type = leaveType;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (joiningDateFrom) params.joining_date_from = joiningDateFrom;
      if (joiningDateTo) params.joining_date_to = joiningDateTo;
      if (includeInactive) params.include_inactive = true;
      if (module) params.module = module;
      if (action) params.action = action;

      switch (reportType) {
        case "employees":
          result = await reportService.getEmployeeReport(params);
          break;
        case "attendance":
          result = await reportService.getAttendanceReport(params);
          break;
        case "leaves":
          result = await reportService.getLeaveReport(params);
          break;
        case "departments":
          result = await reportService.getDepartmentReport(params);
          break;
        case "designations":
          result = await reportService.getDesignationReport(params);
          break;
        case "activity":
          result = await reportService.getActivityReport(params);
          break;
        default:
          throw new Error("Unknown report type");
      }
      setData(result);
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setData(null);
    setPage(1);
    setError(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportType]);

  useEffect(() => {
    setPage(1);
  }, [search, status, departmentId, designationId, employeeId, leaveType, startDate, endDate, joiningDateFrom, joiningDateTo, includeInactive, module, action]);

  useEffect(() => {
    if (page > 1) {
      fetchReport();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const handleGenerate = () => {
    setPage(1);
    fetchReport();
  };

  const handleReset = () => {
    setSearch("");
    setStatus("");
    setDepartmentId("");
    setDesignationId("");
    setEmployeeId("");
    setLeaveType("");
    setStartDate("");
    setEndDate("");
    setJoiningDateFrom("");
    setJoiningDateTo("");
    setIncludeInactive(false);
    setModule("");
    setAction("");
    setPage(1);
    setData(null);
    setError(null);
  };

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = {
        page: 1,
        page_size: 1000,
      };
      if (search) params.search = search;
      if (status) params.status = status;
      if (departmentId) params.department_id = departmentId;
      if (designationId) params.designation_id = designationId;
      if (employeeId) params.employee_id = employeeId;
      if (leaveType) params.leave_type = leaveType;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (joiningDateFrom) params.joining_date_from = joiningDateFrom;
      if (joiningDateTo) params.joining_date_to = joiningDateTo;
      if (includeInactive) params.include_inactive = true;
      if (module) params.module = module;
      if (action) params.action = action;

      let result: ReportResponse;
      switch (reportType) {
        case "employees":
          result = await reportService.getEmployeeReport(params);
          break;
        case "attendance":
          result = await reportService.getAttendanceReport(params);
          break;
        case "leaves":
          result = await reportService.getLeaveReport(params);
          break;
        case "departments":
          result = await reportService.getDepartmentReport(params);
          break;
        case "designations":
          result = await reportService.getDesignationReport(params);
          break;
        case "activity":
          result = await reportService.getActivityReport(params);
          break;
        default:
          throw new Error("Unknown report type");
      }

      if (result.records.length === 0) {
        setError("No data to export.");
        return;
      }

      const columns = Object.keys(result.records[0]).map((key) => ({
        header: key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
        key,
      }));

      exportObjectsToCsv(`${reportType}-report.csv`, result.records, columns);
      toastSuccess("Report exported successfully.");
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const summary = data?.summary;
  const records = data?.records || [];
  const meta = data?.meta;

  const showEmployeeFilters = reportType === "employees";
  const showAttendanceFilters = reportType === "attendance";
  const showLeaveFilters = reportType === "leaves";
  const showDepartmentFilters = reportType === "departments";
  const showDesignationFilters = reportType === "designations";
  const showActivityFilters = reportType === "activity";

  return (
    <div>
      <PageHeader
        title="Reports"
        subtitle="Generate and view management reports."
        actions={
          <div className="flex gap-2">
            <Button variant="ghost" onClick={handleExport} loading={loading} disabled={!data}>
              Export CSV
            </Button>
            <Button onClick={handleGenerate} loading={loading}>
              Generate Report
            </Button>
          </div>
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      <div className="card mb-4 p-4">
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-slate-700">Report Type</label>
          <select
            value={reportType}
            onChange={(e) => setReportType(e.target.value as ReportType)}
            className="input"
          >
            {REPORT_TYPES.map((rt) => (
              <option key={rt.value} value={rt.value}>
                {rt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          {showEmployeeFilters && (
            <>
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="input">
                <option value="">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
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
            </>
          )}
          {showAttendanceFilters && (
            <>
              <Input
                label="Start Date"
                name="start_date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="sm:max-w-xs"
              />
              <Input
                label="End Date"
                name="end_date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="sm:max-w-xs"
              />
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="input">
                <option value="">All Statuses</option>
                <option value="PRESENT">Present</option>
                <option value="ABSENT">Absent</option>
                <option value="HALF_DAY">Half Day</option>
                <option value="LEAVE">Leave</option>
              </select>
            </>
          )}
          {showLeaveFilters && (
            <>
              <Input
                label="Start Date"
                name="start_date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="sm:max-w-xs"
              />
              <Input
                label="End Date"
                name="end_date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="sm:max-w-xs"
              />
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="input">
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
              </select>
              <select value={leaveType} onChange={(e) => setLeaveType(e.target.value)} className="input">
                <option value="">All Leave Types</option>
                <option value="ANNUAL">Annual</option>
                <option value="SICK">Sick</option>
                <option value="CASUAL">Casual</option>
                <option value="UNPAID">Unpaid</option>
              </select>
            </>
          )}
          {showDepartmentFilters && (
            <>
              <Input
                label="Search"
                name="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search departments..."
                className="sm:max-w-xs"
              />
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                />
                Include Inactive
              </label>
            </>
          )}
          {showDesignationFilters && (
            <>
              <Input
                label="Search"
                name="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search designations..."
                className="sm:max-w-xs"
              />
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                />
                Include Inactive
              </label>
            </>
          )}
          {showActivityFilters && (
            <>
              <Input
                label="Module"
                name="module"
                value={module}
                onChange={(e) => setModule(e.target.value)}
                placeholder="e.g. AUTHENTICATION"
                className="sm:max-w-xs"
              />
              <Input
                label="Action"
                name="action"
                value={action}
                onChange={(e) => setAction(e.target.value)}
                placeholder="e.g. LOGIN"
                className="sm:max-w-xs"
              />
            </>
          )}
          <Input
            label="Search"
            name="global_search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={showActivityFilters ? "Search description..." : "Search..."}
            className="sm:max-w-xs"
          />
          <button
            onClick={handleReset}
            className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium"
          >
            Reset
          </button>
        </div>
      </div>

      {loading && !data ? (
        <Loader />
      ) : data && summary ? (
        <>
          <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {(Object.keys(summary) as Array<keyof typeof summary>).map((key) => {
              const value = summary[key];
              if (typeof value !== "number") return null;
              return (
                <div key={key} className="card p-4 text-center">
                  <p className="text-xs uppercase text-slate-500">
                    {key.replace(/_/g, " ")}
                  </p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
                </div>
              );
            })}
          </div>

          {records.length === 0 ? (
            <div className="card p-8 text-center text-sm text-slate-500">
              No records found for the selected filters.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {reportType === "employees" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Email</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Role</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      </>
                    )}
                    {reportType === "attendance" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Date</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      </>
                    )}
                    {reportType === "leaves" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Type</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Dates</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      </>
                    )}
                    {reportType === "departments" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Code</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Employees</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      </>
                    )}
                    {reportType === "designations" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Code</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Employees</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                      </>
                    )}
                    {reportType === "activity" && (
                      <>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Module</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Action</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Description</th>
                        <th className="px-4 py-3 text-left font-medium text-slate-500">Date</th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {records.map((record, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      {reportType === "employees" && (
                        <>
                          <td className="px-4 py-3 font-medium text-slate-900">
                            {(record as { first_name?: string; last_name?: string }).first_name} {(record as { last_name?: string }).last_name}
                          </td>
                          <td className="px-4 py-3 text-slate-600">{(record as { email?: string }).email}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { role?: string }).role}</td>
                          <td className="px-4 py-3">
                            <StatusBadge status={(record as { status?: string }).status} />
                          </td>
                        </>
                      )}
                      {reportType === "attendance" && (
                        <>
                          <td className="px-4 py-3 text-slate-600">{(record as { employee_id?: string }).employee_id}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { date?: string }).date}</td>
                          <td className="px-4 py-3">
                            <StatusBadge status={(record as { status?: string }).status} />
                          </td>
                        </>
                      )}
                      {reportType === "leaves" && (
                        <>
                          <td className="px-4 py-3 text-slate-600">{(record as { employee_name?: string }).employee_name || (record as { employee_id?: string }).employee_id}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { leave_type?: string }).leave_type}</td>
                          <td className="px-4 py-3 text-slate-600">
                            {(record as { start_date?: string }).start_date} to {(record as { end_date?: string }).end_date}
                          </td>
                          <td className="px-4 py-3">
                            <StatusBadge status={(record as { status?: string }).status} />
                          </td>
                        </>
                      )}
                      {reportType === "departments" && (
                        <>
                          <td className="px-4 py-3 font-medium text-slate-900">{(record as { name?: string }).name}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { code?: string }).code}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { employee_count?: number }).employee_count}</td>
                          <td className="px-4 py-3">
                            <StatusBadge status={(record as { is_active?: boolean }).is_active} label={(record as { is_active?: boolean }).is_active ? "Active" : "Inactive"} />
                          </td>
                        </>
                      )}
                      {reportType === "designations" && (
                        <>
                          <td className="px-4 py-3 font-medium text-slate-900">{(record as { name?: string }).name}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { code?: string }).code}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { employee_count?: number }).employee_count}</td>
                          <td className="px-4 py-3">
                            <StatusBadge status={(record as { is_active?: boolean }).is_active} label={(record as { is_active?: boolean }).is_active ? "Active" : "Inactive"} />
                          </td>
                        </>
                      )}
                      {reportType === "activity" && (
                        <>
                          <td className="px-4 py-3 text-slate-600">{(record as { module?: string }).module}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { action?: string }).action}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { description?: string }).description}</td>
                          <td className="px-4 py-3 text-slate-600">{(record as { created_at?: string }).created_at}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {meta && meta.total_pages > 1 && (
            <Pagination
              page={meta.page}
              totalPages={meta.total_pages}
              totalRecords={meta.total_records}
              onPageChange={(nextPage) => setPage(nextPage)}
            />
          )}
        </>
      ) : !loading ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          Select a report type and click Generate to view results.
        </div>
      ) : null}
    </div>
  );
}
