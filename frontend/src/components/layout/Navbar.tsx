/**
 * Navbar.
 * Top navigation bar with user profile image, a dropdown menu with
 * account links (View Profile, Change Password, Logout), and a mobile
 * app name. The dropdown is positioned within the viewport and given a
 * high z-index so it is never clipped by the header.
 */

import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Avatar } from "@/components/common/Avatar";
import {
  ROUTES,
  getChangePasswordNavItem,
  getSetPasswordNavItem,
} from "@/utils/constants";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const changePasswordItem = getChangePasswordNavItem();
  const setPasswordItem = getSetPasswordNavItem();
  const isGoogleUser = user?.login_provider === "GOOGLE";

  // Close the dropdown when clicking outside.
  useEffect(() => {
    const onDocClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const handleLogout = async () => {
    setOpen(false);
    await logout();
    navigate(ROUTES.LOGIN, { replace: true });
  };

  return (
    <header className="relative z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6">
      <div className="md:hidden">
        <span className="text-lg font-semibold text-brand-600">EmpSphere</span>
      </div>

      <div className="ml-auto flex min-w-0 items-center gap-3 sm:gap-4">
        <div className="hidden min-w-0 text-right sm:block">
          <p className="truncate text-sm font-medium text-slate-900">
            {user?.full_name || user?.email}
          </p>
          <p className="truncate text-xs capitalize text-slate-500">
            {user?.role?.toLowerCase().replace("_", " ") || "User"}
          </p>
        </div>

        <div className="relative" ref={menuRef}>
          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            className="flex items-center rounded-full focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
            aria-haspopup="menu"
            aria-expanded={open}
          >
            <Avatar
              name={user?.full_name}
              email={user?.email}
              src={user?.profile_image}
              size="md"
            />
          </button>

          {open ? (
            <div
              role="menu"
              className="absolute right-0 z-50 mt-2 w-64 origin-top-right overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl"
            >
              <div className="border-b border-slate-100 px-4 py-3">
                <p className="truncate text-sm font-semibold text-slate-900">
                  {user?.full_name || user?.email}
                </p>
                <p className="truncate text-xs text-slate-500">{user?.email}</p>
                <p className="mt-1 text-xs capitalize text-brand-600">
                  {user?.role?.toLowerCase().replace("_", " ") || "User"}
                </p>
              </div>

              <Link
                to={ROUTES.PROFILE}
                onClick={() => setOpen(false)}
                className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                role="menuitem"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4"
                  />
                </svg>
                View Profile
              </Link>

               {isGoogleUser ? (
                 <Link
                   to={setPasswordItem.to}
                   onClick={() => setOpen(false)}
                   className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                   role="menuitem"
                 >
                   <svg
                     className="h-4 w-4"
                     fill="none"
                     viewBox="0 0 24 24"
                     strokeWidth={1.5}
                     stroke="currentColor"
                   >
                     <path
                       strokeLinecap="round"
                       strokeLinejoin="round"
                       d={setPasswordItem.icon}
                     />
                   </svg>
                   {setPasswordItem.label}
                 </Link>
               ) : (
                 <Link
                   to={changePasswordItem.to}
                   onClick={() => setOpen(false)}
                   className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                   role="menuitem"
                 >
                   <svg
                     className="h-4 w-4"
                     fill="none"
                     viewBox="0 0 24 24"
                     strokeWidth={1.5}
                     stroke="currentColor"
                   >
                     <path
                       strokeLinecap="round"
                       strokeLinejoin="round"
                       d={changePasswordItem.icon}
                     />
                   </svg>
                   {changePasswordItem.label}
                 </Link>
               )}

               <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                role="menuitem"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                Logout
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
