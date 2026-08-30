/**
 * ActivityLogsPage.
 *
 * Displays a paginated list of activity logs with filters for module,
 * action, and user. Restricted to ADMIN, SUPER_ADMIN, HR_MANAGER, and
 * EMPLOYEE roles. EMPLOYEE sees only their own activity.
 */

import { useEffect, useState, useCallback } from "react";
import { activityLogService } from "@/services/activityLog.service";
import { employeeService } from "@/services/employee.service";
import { PageHeader } from "@/components/common/PageHeader";
import { Input } from "@/components/common/Input";
import { Loader } from "@/components/common/Loader";
import { Pagination } from "@/components/common/Pagination";
import { formatDateTime } from "@/utils/helpers";
import { ActivityLog } from "@/types/activityLog";
import { Employee } from "@/types/employee";
import { useAuth } from "@/hooks/useAuth";
import { ROLES } from "@/utils/constants";

export function ActivityLogsPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [moduleFilter, setModuleFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [employeeFilter, setEmployeeFilter] = useState("");
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [actions, setActions] = useState<string[]>([]);

  const isEmployee = user?.role === ROLES.EMPLOYEE;

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await activityLogService.list({
        module: moduleFilter || undefined,
        action: actionFilter || undefined,
        user_id: employeeFilter || undefined,
        page,
        page_size: 10,
      });
      setLogs(res.logs);
      setTotalPages(res.meta?.total_pages || 0);
      setTotalRecords(res.meta?.total_records || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load activity logs.");
    } finally {
      setLoading(false);
    }
  }, [moduleFilter, actionFilter, employeeFilter, page]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  useEffect(() => {
    setPage(1);
  }, [moduleFilter, actionFilter, employeeFilter]);

  useEffect(() => {
    employeeService.list({ page_size: 1000 }).then((res) => {
      setEmployees(res.employees);
    });
  }, []);

  useEffect(() => {
    activityLogService.distinctActions().then((data) => {
      setActions(data);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title={isEmployee ? "My Activity" : "Activity Logs"}
        subtitle={
          isEmployee
            ? "Track your important actions."
            : "Track important actions across the system."
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end">
        <Input
          label="Module"
          name="module"
          value={moduleFilter}
          onChange={(e) => setModuleFilter(e.target.value)}
          placeholder="e.g. EMPLOYEE"
          className="sm:max-w-xs"
        />
        <div>
          <label className="label" htmlFor="action">
            Action
          </label>
          <select
            id="action"
            name="action"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="input"
          >
            <option value="">All Actions</option>
            {actions.map((act) => (
              <option key={act} value={act}>
                {act}
              </option>
            ))}
          </select>
        </div>
        {!isEmployee && (
          <div>
            <label className="label" htmlFor="employee">
              Employee
            </label>
            <select
              id="employee"
              name="employee"
              value={employeeFilter}
              onChange={(e) => setEmployeeFilter(e.target.value)}
              className="input"
            >
              <option value="">All Employees</option>
              {employees.map((emp) => (
                <option key={emp.user_id} value={emp.user_id}>
                  {emp.first_name} {emp.last_name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading && logs.length === 0 ? (
        <Loader />
      ) : logs.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No activity logs found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Time</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Module</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Action</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Description</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {logs.map((log) => (
                <tr key={log.log_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                    {formatDateTime(log.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                      {log.module}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">{log.action}</td>
                  <td className="px-4 py-3 text-slate-600">{log.description}</td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        log.status === "SUCCESS"
                          ? "text-green-600"
                          : "text-red-600"
                      }
                    >
                      {log.status}
                    </span>
                  </td>
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
          onPageChange={(nextPage) => setPage(nextPage)}
        />
      )}
    </div>
  );
}
