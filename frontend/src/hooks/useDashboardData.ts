import { useState, useCallback, useEffect } from "react";

export function useDashboardData<TStats, TActivities>(options: {
  loadStats: () => Promise<TStats>;
  loadActivities: () => Promise<TActivities>;
}) {
  const [stats, setStats] = useState<TStats | null>(null);
  const [activities, setActivities] = useState<TActivities | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, activitiesData] = await Promise.all([
        options.loadStats(),
        options.loadActivities(),
      ]);
      setStats(statsData);
      setActivities(activitiesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, [options]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    stats: stats ?? ({} as TStats),
    activities: activities ?? ([] as TActivities),
    loading,
    error,
    refresh,
  };
}
