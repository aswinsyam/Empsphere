/**
 * SuperAdminDashboardPage.
 * Dashboard for SUPER_ADMIN users — full access overview.
 */

import { DashboardContent } from "@/components/dashboard/DashboardContent";

const STATS = [
  {
    label: "Total Users",
    value: "—",
    icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4",
  },
  {
    label: "Departments",
    value: "—",
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5",
  },
  {
    label: "Pending Approvals",
    value: "0",
    icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2",
  },
  {
    label: "Active Sessions",
    value: "0",
    icon: "M13 10V3L4 14h7v7l9-11h-7z",
  },
];

const ACTIVITIES = [
  { title: "System seeded with default Super Admin", time: "Today" },
  { title: "Roles and permissions configured", time: "Today" },
  { title: "No recent approvals to review", time: "—" },
];

export function SuperAdminDashboardPage() {
  return (
    <DashboardContent
      title="Welcome to EmpSphere"
      subtitle="Oversee the entire organization — users, roles, departments and future modules all in one place."
      accentClasses="from-indigo-600 via-violet-600 to-purple-600"
      stats={STATS}
      activities={ACTIVITIES}
    />
  );
}
