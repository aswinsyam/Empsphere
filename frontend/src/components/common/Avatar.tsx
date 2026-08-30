/**
 * Avatar.
 *
 * Displays a user's profile image when available, falling back to
 * initials derived from `name` or `email`. Reused in the navbar,
 * dashboard cards, and profile page.
 */

import { cn } from "@/utils/helpers";

interface AvatarProps {
  name?: string | null;
  email?: string | null;
  src?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses: Record<NonNullable<AvatarProps["size"]>, string> = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-16 w-16 text-lg",
};

/** Derive initials (up to two) from a full name or email. */
function getInitials(name?: string | null, email?: string | null): string {
  const source = (name || email || "").trim();
  if (!source) return "?";
  const parts = source.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return source.slice(0, 2).toUpperCase();
}

export function Avatar({
  name,
  email,
  src,
  size = "md",
  className,
}: AvatarProps) {
  /**
   * Displays a user's profile image or initials fallback. Derives
   * initials from `name` or `email` when no image source is provided.
   */
  const initials = getInitials(name, email);

  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-100 font-semibold text-brand-700 ring-2 ring-white",
        sizeClasses[size],
        className
      )}
    >
      {src ? (
        <img
          src={src}
          alt={name || email || "User"}
          className="block h-full w-full min-h-full min-w-full object-cover"
          referrerPolicy="no-referrer"
        />
      ) : (
        <span aria-hidden>{initials}</span>
      )}
    </span>
  );
}

