/**
 * DashboardPage.
 *
 * Single parameterized dashboard for all roles.
 * Each role passes its own stats loader, title, and styling.
 */

import { useCallback, useMemo } from "react";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { statisticsService } from "@/services/statistics.service";
import { activityLogService } from "@/services/activityLog.service";
import { attendanceService } from "@/services/attendance.service";
import { paymentService } from "@/services/payment.service";
import { formatDateTime } from "@/utils/helpers";
import { useDashboardData } from "@/hooks/useDashboardData";
import { useAuth } from "@/hooks/useAuth";
import { StatItem, ActivityItem } from "@/types/dashboard";

interface DashboardConfig {
  title: string;
  subtitle: string;
  accentClasses: string;
  loadStats: (user: any) => Promise<StatItem[]>;
  loadActivities: () => Promise<ActivityItem[]>;
  defaultStats: StatItem[];
}

const DASHBOARD_CONFIGS: Record<string, DashboardConfig> = {
  SUPER_ADMIN: {
    title: "Welcome to EmpSphere",
    subtitle: "Oversee the entire organization — users, roles and future modules all in one place.",
    accentClasses: "from-indigo-600 via-violet-600 to-purple-600",
    loadStats: async () => {
      const data = await statisticsService.getDashboardStats();
      return [
        { label: "Total Employees", value: String(data.total_employees), icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
        { label: "Departments", value: String(data.total_departments), icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
        { label: "Attendance Records", value: String(data.total_attendance), icon: "M9 5H7a2 2 0 00-2 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
        { label: "Pending Leaves", value: String(data.pending_leaves), icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
      ];
    },
    loadActivities: async () => {
      const data = await activityLogService.list({ page_size: 5 });
      const formatted = data.logs.map((log) => ({
        title: log.description,
        time: formatDateTime(log.created_at),
      }));
      return formatted.length > 0 ? formatted : [{ title: "No recent activity.", time: "" }];
    },
    defaultStats: [
      { label: "Total Employees", value: "—", icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
      { label: "Departments", value: "—", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
      { label: "Attendance Records", value: "—", icon: "M9 5H7a2 2 0 00-2 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
      { label: "Pending Leaves", value: "—", icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
    ],
  },
  ADMIN: {
    title: "Welcome back, Admin",
    subtitle: "Manage HR managers and employees, and keep the organization running smoothly.",
    accentClasses: "from-blue-600 via-sky-500 to-cyan-500",
    loadStats: async () => {
      const data = await statisticsService.getDashboardStats();
      return [
        { label: "Team Members", value: String(data.total_employees), icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
        { label: "Pending Leaves", value: String(data.pending_leaves), icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
        { label: "Departments", value: String(data.total_departments), icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
      ];
    },
    loadActivities: async () => {
      const data = await activityLogService.list({ page_size: 5 });
      const formatted = data.logs.map((log) => ({
        title: log.description,
        time: formatDateTime(log.created_at),
      }));
      return formatted.length > 0 ? formatted : [{ title: "No recent activity.", time: "" }];
    },
    defaultStats: [
      { label: "Team Members", value: "—", icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
      { label: "Pending Leaves", value: "—", icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
      { label: "Departments", value: "—", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
    ],
  },
  HR_MANAGER: {
    title: "Welcome, HR Manager",
    subtitle: "Manage the employee lifecycle — profiles, attendance, leaves and more.",
    accentClasses: "from-emerald-600 via-teal-500 to-cyan-500",
    loadStats: async () => {
      const data = await statisticsService.getDashboardStats();
      return [
        { label: "Employees", value: String(data.total_employees), icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
        { label: "Pending Leaves", value: String(data.pending_leaves), icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
        { label: "Departments", value: String(data.total_departments), icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
      ];
    },
    loadActivities: async () => {
      const data = await activityLogService.list({ page_size: 5 });
      const formatted = data.logs.map((log) => ({
        title: log.description,
        time: formatDateTime(log.created_at),
      }));
      return formatted.length > 0 ? formatted : [{ title: "No recent activity.", time: "" }];
    },
    defaultStats: [
      { label: "Employees", value: "—", icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
      { label: "Pending Leaves", value: "—", icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
      { label: "Departments", value: "—", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
    ],
  },
  EMPLOYEE: {
    title: "Welcome back",
    subtitle: "View your profile, track your attendance and manage your leave requests.",
    accentClasses: "from-sky-600 via-blue-500 to-indigo-500",
    loadStats: async (user: any) => {
      if (!user?._id) {
        return [
          { label: "My Profile", value: user?.full_name || user?.email || "—", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
          { label: "Days Present", value: "—", icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" },
        ];
      }
      const [summary, payments] = await Promise.all([
        attendanceService.summary(user._id),
        paymentService.getMyPayments({ page_size: 1 }).then((res) => res.payments[0] || null).catch(() => null),
      ]);
      const stats: StatItem[] = [
        { label: "My Profile", value: user.full_name || user.email || "—", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
        { label: "Days Present", value: String(summary.present_days ?? 0), icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" },
      ];
      if (payments) {
        stats.push({
          label: "Recent Payment",
          value: `₹${payments.amount.toFixed(2)}`,
          icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z",
        });
      }
      return stats;
    },
    loadActivities: async () => {
      const data = await activityLogService.list({ page_size: 5 });
      const formatted = data.logs.map((log) => ({
        title: log.description,
        time: formatDateTime(log.created_at),
      }));
      return formatted.length > 0 ? formatted : [{ title: "No recent activity.", time: "" }];
    },
    defaultStats: [
      { label: "My Profile", value: "—", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
      { label: "Days Present", value: "—", icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" },
    ],
  },
};

export function DashboardPage({ role }: { role: string }) {
  const { user } = useAuth();
  const config = DASHBOARD_CONFIGS[role];

  const loadStats = useCallback(async (): Promise<StatItem[]> => {
    return config.loadStats(user);
  }, [user?._id, user?.full_name, user?.email]);

  const loadActivities = useCallback(async (): Promise<ActivityItem[]> => {
    return config.loadActivities();
  }, []);

  const { stats, activities, loading } = useDashboardData({
    loadStats,
    loadActivities,
  });

  const defaultActivities = useMemo<ActivityItem[]>(() => [], []);

  return (
    <DashboardContent
      title={config.title}
      subtitle={config.subtitle}
      accentClasses={config.accentClasses}
      stats={loading ? config.defaultStats : stats}
      activities={loading ? defaultActivities : activities}
    />
  );
}
