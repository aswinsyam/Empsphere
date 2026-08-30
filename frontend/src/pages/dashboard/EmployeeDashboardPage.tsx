/**
 * EmployeeDashboardPage.
 *
 * Dashboard for `EMPLOYEE` users. Shows personal stats (profile,
 * attendance, leave balance, payments) and a limited activity feed.
 */

import { useCallback, useMemo } from "react";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { attendanceService } from "@/services/attendance.service";
import { activityLogService } from "@/services/activityLog.service";
import { paymentService } from "@/services/payment.service";
import { formatDateTime } from "@/utils/helpers";
import { useDashboardData } from "@/hooks/useDashboardData";
import { useAuth } from "@/hooks/useAuth";
import { StatItem, ActivityItem } from "@/types/dashboard";

export function EmployeeDashboardPage() {
  const { user } = useAuth();

  const loadStats = useCallback(async (): Promise<StatItem[]> => {
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
  }, [user?._id, user?.full_name, user?.email]);

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
    { label: "My Profile", value: "—", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
    { label: "Days Present", value: "—", icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" },
  ], []);

  const defaultActivities = useMemo<ActivityItem[]>(() => [], []);

  return (
    <DashboardContent
      title="Welcome back"
      subtitle="View your profile, track your attendance and manage your leave requests."
      accentClasses="from-sky-600 via-blue-500 to-indigo-500"
      stats={loading ? defaultStats : stats}
      activities={loading ? defaultActivities : activities}
    />
  );
}
