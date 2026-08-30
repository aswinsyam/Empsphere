/**
 * useDashboardData hook.
 *
 * Shared data-loading logic for all role dashboards.
 * Loads statistics and recent activity, handling cancellation
 * and error states consistently.
 */

import { useEffect, useState } from "react";
import { StatItem, ActivityItem } from "@/types/dashboard";

export interface UseDashboardDataOptions {
  /** Function that returns the stats array for this role. */
  loadStats: () => Promise<StatItem[]>;
  /** Function that returns the activities array for this role. */
  loadActivities: () => Promise<ActivityItem[]>;
}

export function useDashboardData(options: UseDashboardDataOptions) {
  const { loadStats, loadActivities } = options;
  const [stats, setStats] = useState<StatItem[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsData, activitiesData] = await Promise.all([
          loadStats(),
          loadActivities(),
        ]);
        if (!cancelled) {
          setStats(statsData);
          setActivities(activitiesData);
        }
      } catch (err) {
        if (!cancelled) {
          setError("Failed to load dashboard data.");
          setActivities([{ title: "Failed to load dashboard data.", time: "" }]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [loadStats, loadActivities]);

  return { stats, activities, loading, error };
}
