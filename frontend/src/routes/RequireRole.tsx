/**
 * RequireRole.
 * Route guard that restricts access based on the authenticated user's role.
 * Redirects unauthorized users to the /unauthorized page.
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
