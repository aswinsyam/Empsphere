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

/**
 * Roles allowed to access the Employee Management module
 * (list, detail, create, edit).
 *
 * Mirrors the backend `@require_role(*EMPLOYEE_MANAGER_ROLES)` rule on
 * `EmployeeController`. EMPLOYEE is intentionally excluded. Single source of
 * truth for both route guards (`RequireRole`) and in-page action visibility,
 * so the rule is never duplicated.
 */
export const EMPLOYEE_MANAGEMENT_ROLES: RoleKey[] = [
  ROLES.SUPER_ADMIN,
  ROLES.ADMIN,
  ROLES.HR_MANAGER,
];

/** Return true when the role may access/manage Employee Management. */
export function canManageEmployees(role?: string | null): boolean {
  return Boolean(role) && EMPLOYEE_MANAGEMENT_ROLES.includes(role as RoleKey);
}

/** Route paths used by the app. */
export const ROUTES = {
  LOGIN: "/login",
  REGISTER: "/register",
  VERIFY_EMAIL: "/verify-email",
  VERIFY_OTP: "/verify-otp",
  DASHBOARD: "/dashboard",
  CHANGE_PASSWORD: "/change-password",
  SET_PASSWORD: "/set-password",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  PROFILE: "/profile",
  UNAUTHORIZED: "/unauthorized",
  EMPLOYEES: "/employees",
  DEPARTMENTS: "/departments",
  ATTENDANCE: "/attendance",
  LEAVES: "/leaves",
  ACTIVITY_LOGS: "/activity-logs",
  DESIGNATIONS: "/designations",
  PAYMENTS: "/payments",
  REPORTS: "/reports",

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
  employees: {
    label: "Employees",
    to: ROUTES.EMPLOYEES,
    icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4m8 0a4 4 0 11-4-4",
  },
  departments: {
    label: "Departments",
    to: ROUTES.DEPARTMENTS,
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
  },
  attendance: {
    label: "Attendance",
    to: ROUTES.ATTENDANCE,
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  leave: {
    label: "Leave",
    to: ROUTES.LEAVES,
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  payments: {
    label: "Payments",
    to: ROUTES.PAYMENTS,
    icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z",
  },
  reports: {
    label: "Reports",
    to: ROUTES.REPORTS,
    icon: "M9 17v-6m4 6V7m4 10v-3M3 21h18M4 4h16v14a2 2 0 01-2 2H6a2 2 0 01-2-2V4z",
  },
  changePassword: {
    label: "Change Password",
    to: ROUTES.CHANGE_PASSWORD,
    icon: "M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z",
  },
  activityLogs: {
    label: "Activity Logs",
    to: ROUTES.ACTIVITY_LOGS,
    icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  designations: {
    label: "Designations",
    to: ROUTES.DESIGNATIONS,
    icon: "M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4",
  },
};

/** Nav items for the Super Admin dashboard. */
export const SUPER_ADMIN_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.employees,
  baseNav.departments,
  baseNav.designations,
  baseNav.attendance,
  baseNav.leave,
  baseNav.activityLogs,
  baseNav.payments,
  baseNav.reports,
];

/** Nav items for the Admin dashboard. */
export const ADMIN_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.employees,
  baseNav.departments,
  baseNav.designations,
  baseNav.attendance,
  baseNav.leave,
  baseNav.activityLogs,
  baseNav.payments,
  baseNav.reports,
];

/** Nav items for the HR Manager dashboard. */
export const HR_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.employees,
  baseNav.departments,
  baseNav.designations,
  baseNav.attendance,
  baseNav.leave,
  baseNav.activityLogs,
  baseNav.payments,
  baseNav.reports,
];

/** Nav items for the Employee dashboard. */
export const EMPLOYEE_NAV: NavItem[] = [
  baseNav.dashboard,
  baseNav.attendance,
  baseNav.leave,
  baseNav.payments,
  {
    label: "My Activity",
    to: ROUTES.ACTIVITY_LOGS,
    icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
  },
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
