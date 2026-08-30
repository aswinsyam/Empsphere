/**
 * DashboardRedirect.
 *
 * Redirects from the generic `/dashboard` path to the role-specific
 * dashboard route based on the authenticated user's role, ensuring
 * users land on the correct dashboard without manual routing logic.
 */

import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { getDashboardRoute } from "@/utils/constants";

export function DashboardRedirect() {
  /**
   * Resolves the correct dashboard route for the current user's role
   * and performs a client-side redirect.
   */
  const { user } = useAuth();
  const route = getDashboardRoute(user?.role);
  return <Navigate to={route} replace />;
}

