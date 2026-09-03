/**
 * StatusBadge.
 *
 * Reusable badge for displaying status values with consistent coloring.
 */

import { cn } from "@/utils/helpers";

interface StatusBadgeProps {
  /** Raw status value to display. */
  status?: string | boolean | null;
  /** Optional label override. */
  label?: string;
}

const STATUS_MAP: Record<string, { className: string; label: string }> = {
  ACTIVE: { className: "bg-green-100 text-green-700", label: "Active" },
  true: { className: "bg-green-100 text-green-700", label: "Active" },
  PRESENT: { className: "bg-green-100 text-green-700", label: "Present" },
  APPROVED: { className: "bg-green-100 text-green-700", label: "Approved" },
  INACTIVE: { className: "bg-slate-100 text-slate-600", label: "Inactive" },
  false: { className: "bg-slate-100 text-slate-600", label: "Inactive" },
  ABSENT: { className: "bg-red-100 text-red-700", label: "Absent" },
  REJECTED: { className: "bg-red-100 text-red-700", label: "Rejected" },
  HALF_DAY: { className: "bg-amber-100 text-amber-700", label: "Half Day" },
  PENDING: { className: "bg-amber-100 text-amber-700", label: "Pending" },
};

const DEFAULT_CLASS = "bg-slate-100 text-slate-600";

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const key = status === undefined || status === null ? "" : String(status);
  const mapped = STATUS_MAP[key];
  const displayLabel = label || mapped?.label || key || "Unknown";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        mapped?.className || DEFAULT_CLASS
      )}
    >
      {displayLabel}
    </span>
  );
}