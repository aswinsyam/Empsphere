/**
 * DashboardPage.
 * Landing screen for authenticated users.
 */

import { useAuth } from "@/hooks/useAuth";

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">
        Welcome, {user?.full_name || user?.email}
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Here&apos;s an overview of your workspace.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-5">
          <p className="text-sm text-slate-500">Departments</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">—</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Employees</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">—</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Pending Approvals</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">0</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Notifications</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">0</p>
        </div>
      </div>
    </div>
  );
}
