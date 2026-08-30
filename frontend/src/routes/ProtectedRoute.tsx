/**
 * ProtectedRoute.
 *
 * Route guard that checks whether the user is authenticated.
 * While auth state is being restored from storage it shows a `Loader`;
 * otherwise it redirects unauthenticated users to `/login` while
 * remembering the attempted destination.
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Loader } from "@/components/common/Loader";

export function ProtectedRoute() {
  /**
   * Redirects unauthenticated users to `/login`, preserving the attempted
   * location in router state so they can be sent back after login.
   * Renders a `Loader` while the auth state is being restored.
   */
  const { isAuthenticated, initializing } = useAuth();
  const location = useLocation();

  if (initializing) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
