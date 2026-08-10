/**
 * HRDashboardPage.
 * Dashboard for HR_MANAGER users — manages employees.
 */

import { DashboardContent } from "@/components/dashboard/DashboardContent";

const STATS = [
  {
    label: "Employees",
    value: "—",
    icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4",
  },
  {
    label: "Departments",
    value: "—",
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5",
  },
  {
    label: "On Leave Today",
    value: "0",
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  {
    label: "Pending Reviews",
    value: "0",
    icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2",
  },
];

const ACTIVITIES = [
  { title: "Employee management coming in Week 2", time: "Soon" },
  { title: "No pending leave requests", time: "—" },
  { title: "Departments overview ready", time: "Today" },
];

export function HRDashboardPage() {
  return (
    <DashboardContent
      title="Welcome, HR Manager"
      subtitle="Manage the employee lifecycle — profiles, attendance, leaves and more."
      accentClasses="from-emerald-600 via-teal-500 to-cyan-500"
      stats={STATS}
      activities={ACTIVITIES}
    />
  );
}
