/**
 * UnauthorizedPage.
 *
 * 403 error screen. Shown when an authenticated user lacks the required
 * role for a protected route. Provides a link back to the dashboard.
 */

import { Link } from "react-router-dom";

export function UnauthorizedPage() {
  /**
   * Renders a 403 error page when an authenticated user lacks the
   * required role for a protected route. Includes a link back to the
   * dashboard.
   */
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 text-center">
      <p className="text-6xl font-bold text-brand-600">403</p>
      <h1 className="mt-4 text-2xl font-semibold text-slate-900">
        Access denied
      </h1>
      <p className="mt-2 text-sm text-slate-500">
        You don&apos;t have permission to view this page.
      </p>
      <Link
        to="/dashboard"
        className="mt-6 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
      >
        Go to dashboard
      </Link>
    </div>
  );
}
