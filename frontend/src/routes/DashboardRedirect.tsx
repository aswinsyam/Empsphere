/**
 * DashboardRedirect.
 * Redirects from the generic `/dashboard` path to the role-specific
 * dashboard route based on the authenticated user's role.
 */

import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { getDashboardRoute } from "@/utils/constants";

export function DashboardRedirect() {
  const { user } = useAuth();
  const route = getDashboardRoute(user?.role);
  return <Navigate to={route} replace />;
}

