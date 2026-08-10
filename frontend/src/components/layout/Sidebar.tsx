/**
 * Sidebar.
 * Role-aware navigation sidebar shown inside the dashboard layout.
 * Placeholder links for future modules (Week 2+) are hidden or shown
 * based on the authenticated user's role.
 */

import { NavLink } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/utils/helpers";
import { APP_NAME, getNavItems, PLACEHOLDER_ROUTE } from "@/utils/constants";

export function Sidebar() {
  const { user } = useAuth();
  const navItems = getNavItems(user?.role);

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col">
      <div className="flex h-16 items-center border-b border-slate-200 px-6">
        <span className="text-xl font-semibold text-brand-600">{APP_NAME}</span>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navItems.map((item) => {
          const isPlaceholder = item.to === PLACEHOLDER_ROUTE;
          return (
            <NavLink
              key={item.label}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                  isPlaceholder && "bg-slate-50 text-slate-400",
                  isPlaceholder && "cursor-default"
                )
              }
              onClick={(event) => {
                if (isPlaceholder) event.preventDefault();
              }}
              aria-disabled={isPlaceholder}
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
                  d={item.icon}
                />
              </svg>
              {item.label}
              {isPlaceholder ? (
                <span className="ml-auto rounded bg-slate-200 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-slate-500">
                  Soon
                </span>
              ) : null}
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 p-4">
        <p className="text-xs text-slate-400">
          {user?.role?.toLowerCase().replace("_", " ")} workspace
        </p>
      </div>
    </aside>
  );
}
