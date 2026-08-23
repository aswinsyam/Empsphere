/**
 * DashboardContent.
 *
 * Shared dashboard shell used by all four role dashboards. Composes
 * a welcome banner, user profile card, statistics grid, and a recent
 * activity feed. Each role dashboard passes its own title, accent
 * gradient, stats, and activities.
 */

import { useAuth } from "@/hooks/useAuth";
import { Avatar } from "@/components/common/Avatar";
import { cn, getProfileImageUrl } from "@/utils/helpers";

/** A single statistics card definition. */
export interface StatCard {
  label: string;
  value: string | number;
  icon: string;
  accent?: string;
}

/** A single recent-activity row. */
export interface ActivityItem {
  title: string;
  time: string;
}

interface DashboardContentProps {
  /** Page heading shown in the welcome card. */
  title: string;
  /** Subtitle shown under the heading. */
  subtitle: string;
  /** Accent gradient classes for the welcome banner. */
  accentClasses?: string;
  /** Statistics cards to render (placeholder values). */
  stats: StatCard[];
  /** Recent activity placeholder rows. */
  activities: ActivityItem[];
}

const DEFAULT_ACCENT =
  "from-brand-600 via-brand-500 to-indigo-500";

export function DashboardContent({
  title,
  subtitle,
  accentClasses,
  stats,
  activities,
}: DashboardContentProps) {
  /**
   * Shared dashboard shell. Composes a welcome banner, user profile
   * card, statistics grid, and recent activity feed. Each role dashboard
   * passes its own configuration to this component.
   */
  const { user } = useAuth();

  const displayName = user?.full_name || user?.email || "User";
  const roleLabel = user?.role?.toLowerCase().replace("_", " ") || "user";

  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      <div
        className={cn(
          "relative overflow-hidden rounded-2xl bg-gradient-to-r p-6 text-white shadow-card sm:p-8",
          accentClasses || DEFAULT_ACCENT
        )}
      >
        <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/10" />
        <div className="absolute -bottom-12 right-16 h-32 w-32 rounded-full bg-white/10" />
        <h1 className="text-2xl font-bold sm:text-3xl">{title}</h1>
        <p className="mt-2 max-w-xl text-sm text-white/85 sm:text-base">
          {subtitle}
        </p>
      </div>

      {/* User profile card */}
      <div className="card flex flex-col gap-4 p-6 sm:flex-row sm:items-center">
        <Avatar
          name={user?.full_name}
          email={user?.email}
          src={getProfileImageUrl(user?._id, user?.profile_image_id)}
          size="lg"
        />
        <div className="min-w-0 flex-1">
          <p className="text-lg font-semibold text-slate-900">{displayName}</p>
          <p className="text-sm capitalize text-slate-500">{roleLabel}</p>
          <p className="mt-1 truncate text-sm text-slate-500">{user?.email}</p>
        </div>
        <div className="flex flex-wrap gap-6 text-sm">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Employee Code
            </p>
            <p className="mt-0.5 font-medium text-slate-800">
              {user?.employee_code || "-"}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Email Verified
            </p>
            <p className="mt-0.5 font-medium text-slate-800">
              {user?.is_email_verified ? "Yes" : "No"}
            </p>
          </div>
        </div>
      </div>

      {/* Statistics cards (placeholder values) */}
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Overview
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="card p-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">{stat.label}</span>
                <span
                  className={cn(
                    "inline-flex h-9 w-9 items-center justify-center rounded-lg",
                    stat.accent || "bg-brand-50 text-brand-600"
                  )}
                >
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d={stat.icon}
                    />
                  </svg>
                </span>
              </div>
              <p className="mt-3 text-3xl font-semibold text-slate-900">
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div className="card p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Recent Activity
        </h2>
        {activities.length === 0 ? (
          <p className="text-sm text-slate-500">No recent activity.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {activities.map((activity, index) => (
              <li
                key={index}
                className="flex items-center justify-between gap-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-brand-500" />
                  <span className="text-sm text-slate-700">
                    {activity.title}
                  </span>
                </div>
                <span className="text-xs text-slate-400">{activity.time}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
