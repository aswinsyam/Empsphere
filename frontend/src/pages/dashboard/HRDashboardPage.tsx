/**
 * HRDashboardPage.
 *
 * Dashboard for `HR_MANAGER` users. Provides employee-lifecycle
 * management context with live stats and activity feed.
 */

import { useCallback, useMemo } from "react";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { statisticsService } from "@/services/statistics.service";
import { activityLogService } from "@/services/activityLog.service";
import { formatDateTime } from "@/utils/helpers";
import { useDashboardData } from "@/hooks/useDashboardData";
import { StatItem, ActivityItem } from "@/types/dashboard";

export function HRDashboardPage() {
  const loadStats = useCallback(async (): Promise<StatItem[]> => {
    const data = await statisticsService.getDashboardStats();
    return [
      { label: "Employees", value: String(data.total_employees), icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
      { label: "Pending Leaves", value: String(data.pending_leaves), icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
      { label: "Departments", value: String(data.total_departments), icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
    ];
  }, []);

  const loadActivities = useCallback(async (): Promise<ActivityItem[]> => {
    const data = await activityLogService.list({ page_size: 5 });
    const formatted = data.logs.map((log) => ({
      title: log.description,
      time: formatDateTime(log.created_at),
    }));
    return formatted.length > 0 ? formatted : [{ title: "No recent activity.", time: "" }];
  }, []);

  const { stats, activities, loading } = useDashboardData({
    loadStats,
    loadActivities,
  });

  const defaultStats = useMemo<StatItem[]>(() => [
    { label: "Employees", value: "—", icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4" },
    { label: "Pending Leaves", value: "—", icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2 2V9a2 2 0 012-2z" },
    { label: "Departments", value: "—", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
  ], []);

  const defaultActivities = useMemo<ActivityItem[]>(() => [
    { title: "Loading dashboard data...", time: "" },
  ], []);

  return (
    <DashboardContent
      title="Welcome, HR Manager"
      subtitle="Manage the employee lifecycle — profiles, attendance, leaves and more."
      accentClasses="from-emerald-600 via-teal-500 to-cyan-500"
      stats={loading ? defaultStats : stats}
      activities={loading ? defaultActivities : activities}
    />
  );
}
