/**
 * RequireRole.
 *
 * Route guard that restricts access based on the authenticated user's role.
 * If the user's role is not in the allowed list, they are redirected to
 * their own dashboard (or `/login` if unauthenticated). Renders `null`
 * while auth state is initializing.
 */

import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { ROLE_DASHBOARD_ROUTES, RoleKey } from "@/utils/constants";

interface RequireRoleProps {
  /** Roles allowed to access this route. */
  roles: RoleKey[];
  /** Fallback path when the user's role is not allowed. */
  children: React.ReactNode;
}

export function RequireRole({ roles, children }: RequireRoleProps) {
  /**
   * Redirects authenticated-but-unauthorized users to their own role's
   * dashboard. Unauthenticated users are sent to `/login`. Renders
   * `null` while auth state is initializing.
   */
  const { user, initializing } = useAuth();
  const location = useLocation();

  if (initializing) {
    return null;
  }

  const role = user?.role as RoleKey | undefined;

  if (!role || !roles.includes(role)) {
    // Redirect an authenticated-but-unauthorized user to their own dashboard.
    const fallback = role ? ROLE_DASHBOARD_ROUTES[role] : "/login";
    return <Navigate to={fallback} replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
