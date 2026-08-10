/**
 * AdminDashboardPage.
 * Dashboard for ADMIN users — manages HR managers and employees.
 */

import { DashboardContent } from "@/components/dashboard/DashboardContent";

const STATS = [
  {
    label: "Team Members",
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
    label: "Open Requests",
    value: "0",
    icon: "M8 10h8m-8 4h5m-2.5 7a9 9 0 100-18 9 9 0 000 18z",
  },
];

const ACTIVITIES = [
  { title: "HR Managers and employees management coming in Week 2", time: "Soon" },
  { title: "No pending approvals", time: "—" },
  { title: "Departments overview ready", time: "Today" },
];

export function AdminDashboardPage() {
  return (
    <DashboardContent
      title="Welcome back, Admin"
      subtitle="Manage HR managers and employees, and keep the organization running smoothly."
      accentClasses="from-blue-600 via-sky-500 to-cyan-500"
      stats={STATS}
      activities={ACTIVITIES}
    />
  );
}
