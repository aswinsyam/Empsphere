/**
 * Dashboard types.
 * Shared interfaces for dashboard statistics and activity items.
 */

/** A single statistics card on the dashboard. */
export interface StatItem {
  label: string;
  value: string | number;
  icon: string;
  accent?: string;
}

/** A single recent-activity row on the dashboard. */
export interface ActivityItem {
  title: string;
  time: string;
}
