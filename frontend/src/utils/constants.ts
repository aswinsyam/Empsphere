/**
 * Shared constants used across the frontend.
 */

/** System role names (must match the backend Role enum). */
export const ROLES = {
  EMPLOYEE: "EMPLOYEE",
  HR_MANAGER: "HR_MANAGER",
  ADMIN: "ADMIN",
  SUPER_ADMIN: "SUPER_ADMIN",
} as const;

export type RoleKey = (typeof ROLES)[keyof typeof ROLES];

/** Route paths used by the app. */
export const ROUTES = {
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
VERIFY_EMAIL: "/verify-email",
  DASHBOARD: "/dashboard",
  CHANGE_PASSWORD: "/change-password",
  SET_PASSWORD: "/set-password",
  PROFILE: "/profile",
  UNAUTHORIZED: "/unauthorized",
  CREATE_USER: "/users/create",

  // Role-specific dashboards
  DASHBOARD_SUPER_ADMIN: "/dashboard/super-admin",
  DASHBOARD_ADMIN: "/dashboard/admin",
  DASHBOARD_HR: "/dashboard/hr",
  DASHBOARD_EMPLOYEE: "/dashboard/employee",
} as const;

/** Role → dashboard route mapping. */
export const ROLE_DASHBOARD_ROUTES: Record<RoleKey, string> = {
  [ROLES.SUPER_ADMIN]: ROUTES.DASHBOARD_SUPER_ADMIN,
  [ROLES.ADMIN]: ROUTES.DASHBOARD_ADMIN,
  [ROLES.HR_MANAGER]: ROUTES.DASHBOARD_HR,
  [ROLES.EMPLOYEE]: ROUTES.DASHBOARD_EMPLOYEE,
};

/**
 * Resolve the dashboard route for a given role.
 * Falls back to the generic dashboard when the role is unknown.
 */
export function getDashboardRoute(role?: string | null): string {
  if (role && role in ROLE_DASHBOARD_ROUTES) {
    return ROLE_DASHBOARD_ROUTES[role as RoleKey];
  }
  return ROUTES.DASHBOARD;
}

/** App name. */
export const APP_NAME = "EmpSphere";

/** Default token expiry check (ms). */
export const TOKEN_EXPIRY_BUFFER_MS = 30 * 1000; // 30 seconds

/** Placeholder route used for future modules (Week 2+). */
export const PLACEHOLDER_ROUTE = "#";

/**
 * Sidebar navigation definitions per role.
 * Each item is a placeholder link for a future module (Week 2+).
 */
export interface NavItem {
  label: string;
  to: string;
  icon: string;
}

const baseNav = {
  dashboard: {
    label: "Dashboard",
    to: ROUTES.DASHBOARD,
    icon: "M3 12l9-9 9 9M5 10v10h14V10",
  },
  departments: {
    label: "Departments",
    to: "/departments",
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5",
  },
  employees: {
    label: "Employees",
    to: PLACEHOLDER_ROUTE,
    icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4",
  },
  attendance: {
    label: "Attendance",
    to: PLACEHOLDER_ROUTE,
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  leave: {
    label: "Leave",
    to: PLACEHOLDER_ROUTE,
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  payroll: {
    label: "Payroll",
    to: PLACEHOLDER_ROUTE,
    icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  reports: {
    label: "Reports",
    to: PLACEHOLDER_ROUTE,
    icon: "M9 17v-6m4 6V7m4 10v-3M3 21h18M4 4h16v14a2 2 0 01-2 2H6a2 2 0 01-2-2V4z",
  },
changePassword: {
    label: "Change Password",
    to: ROUTES.CHANGE_PASSWORD,
    icon: "M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z",
  },
  createUser: {
    label: "Create User",
    to: ROUTES.CREATE_USER,
    icon: "M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z",
  },
};

/** Nav items for the Super Admin dashboard. */
export const SUPER_ADMIN_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.createUser,
  baseNav.departments,
  baseNav.employees,
  baseNav.attendance,
  baseNav.leave,
  baseNav.payroll,
  baseNav.reports,
];

/** Nav items for the Admin dashboard. */
export const ADMIN_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.createUser,
  baseNav.departments,
  baseNav.employees,
  baseNav.attendance,
  baseNav.leave,
  baseNav.payroll,
  baseNav.reports,
];

/** Nav items for the HR Manager dashboard. */
export const HR_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.createUser,
  baseNav.departments,
  baseNav.employees,
  baseNav.attendance,
  baseNav.leave,
];

/** Nav items for the Employee dashboard. */
export const EMPLOYEE_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.attendance,
  baseNav.leave,
  baseNav.payroll,
];

/** Resolve the nav items for a given role. */
export function getNavItems(role?: string | null): NavItem[] {
  switch (role) {
    case ROLES.SUPER_ADMIN:
      return SUPER_ADMIN_NAV;
    case ROLES.ADMIN:
      return ADMIN_NAV;
    case ROLES.HR_MANAGER:
      return HR_NAV;
    case ROLES.EMPLOYEE:
      return EMPLOYEE_NAV;
    default:
      return [baseNav.dashboard];
  }
}

/** Resolve the Change Password nav item. */
export function getChangePasswordNavItem(): NavItem {
  return baseNav.changePassword;
}

/** Resolve the Set Password nav item (for Google users without a local password). */
export function getSetPasswordNavItem(): NavItem {
  return {
    label: "Set Password",
    to: ROUTES.SET_PASSWORD,
    icon: "M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z",
  };
}
