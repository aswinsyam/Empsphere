/**
 * EmployeeDashboardPage.
 * Dashboard for EMPLOYEE users — access to their own profile only.
 */

import { DashboardContent } from "@/components/dashboard/DashboardContent";

const STATS = [
  {
    label: "My Profile",
    value: "—",
    icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
  },
  {
    label: "Days Present",
    value: "0",
    icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  {
    label: "Leave Balance",
    value: "0",
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  {
    label: "Next Payslip",
    value: "—",
    icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
];

const ACTIVITIES = [
  { title: "Welcome to your personal dashboard", time: "Today" },
  { title: "Attendance and leave tracking coming in Week 2", time: "Soon" },
  { title: "Your profile is up to date", time: "—" },
];

export function EmployeeDashboardPage() {
  return (
    <DashboardContent
      title="Welcome back"
      subtitle="View your profile, track your attendance and manage your leave requests."
      accentClasses="from-sky-600 via-blue-500 to-indigo-500"
      stats={STATS}
      activities={ACTIVITIES}
    />
  );
}
