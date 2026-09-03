/**
 * DashboardLayout.
 *
 * Shell component for all protected pages. Renders the `Sidebar` and
 * `Navbar`, then uses React Router's `Outlet` to render the matched
 * child route in the main content area.
 */

import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";

export function DashboardLayout() {
  /**
   * Dashboard shell combining `Sidebar`, `Navbar`, and a main content
   * area rendered via React Router's `Outlet`.
   */
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
