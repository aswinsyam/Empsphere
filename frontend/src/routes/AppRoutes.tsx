/**
 * AppRoutes.
 *
 * Route configuration layer. Declares all public, protected, and error
 * routes for the application. Protected routes are wrapped in
 * `ProtectedRoute` (auth check) and `DashboardLayout` (sidebar + navbar),
 * while role-specific dashboards add an additional `RequireRole` guard.
 */

import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "./ProtectedRoute";
import { RequireRole } from "./RequireRole";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { VerifyEmailPage } from "@/pages/auth/VerifyEmailPage";
import { ChangePasswordPage } from "@/pages/auth/ChangePasswordPage";
import { SetPasswordPage } from "@/pages/auth/SetPasswordPage";
import { ForgotPasswordPage } from "@/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/auth/ResetPasswordPage";
import { ProfilePage } from "@/pages/profile/ProfilePage";
import { DashboardRedirect } from "./DashboardRedirect";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { EmployeesPage } from "@/pages/employees/EmployeesPage";
import { EmployeeDetailPage } from "@/pages/employees/EmployeeDetailPage";
import { AttendancePage } from "@/pages/attendance/AttendancePage";
import { LeavesPage } from "@/pages/leaves/LeavesPage";
import { ActivityLogsPage } from "@/pages/activityLogs/ActivityLogsPage";
import { DepartmentsPage } from "@/pages/departments/DepartmentsPage";
import { DepartmentDetailPage } from "@/pages/departments/DepartmentDetailPage";
import { DesignationsPage } from "@/pages/designations/DesignationsPage";
import { PaymentsPage } from "@/pages/payments/PaymentsPage";
import { ReportsPage } from "@/pages/reports/ReportsPage";
import { NotFoundPage } from "@/pages/errors/NotFoundPage";
import { UnauthorizedPage } from "@/pages/errors/UnauthorizedPage";
import { HomePage } from "@/pages/public/HomePage";
import { AboutPage } from "@/pages/public/AboutPage";
import { ContactPage } from "@/pages/public/ContactPage";
import { TermsPage } from "@/pages/public/TermsPage";
import { PrivacyPage } from "@/pages/public/PrivacyPage";
import { CancellationRefundPage } from "@/pages/public/CancellationRefundPage";
import { ShippingPolicyPage } from "@/pages/public/ShippingPolicyPage";
import { ROLES, EMPLOYEE_MANAGEMENT_ROLES } from "@/utils/constants";

export function AppRoutes() {
  /**
   * Declares all application routes. Public routes are placed at the top
   * level. Protected routes are wrapped in `ProtectedRoute` and
   * `DashboardLayout`. Role-specific dashboards are further guarded by
   * `RequireRole` to prevent unauthorized access.
   */
  return (
    <Routes>
      {/* Public/auth routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/verify-otp" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<DashboardRedirect />} />
          <Route
            path="/dashboard/super-admin"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN]}>
                <DashboardPage role={ROLES.SUPER_ADMIN} />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/admin"
            element={
              <RequireRole roles={[ROLES.ADMIN]}>
                <DashboardPage role={ROLES.ADMIN} />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/hr"
            element={
              <RequireRole roles={[ROLES.HR_MANAGER]}>
                <DashboardPage role={ROLES.HR_MANAGER} />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/employee"
            element={
              <RequireRole roles={[ROLES.EMPLOYEE]}>
                <DashboardPage role={ROLES.EMPLOYEE} />
              </RequireRole>
            }
          />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/set-password" element={<SetPasswordPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route
            path="/employees"
            element={
              <RequireRole roles={EMPLOYEE_MANAGEMENT_ROLES}>
                <EmployeesPage />
              </RequireRole>
            }
          />
          <Route
            path="/employees/:id"
            element={
              <RequireRole roles={EMPLOYEE_MANAGEMENT_ROLES}>
                <EmployeeDetailPage />
              </RequireRole>
            }
          />
          <Route path="/attendance" element={<AttendancePage />} />
          <Route path="/leaves" element={<LeavesPage />} />
          <Route
            path="/activity-logs"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER, ROLES.EMPLOYEE]}>
                <ActivityLogsPage />
              </RequireRole>
            }
          />
          <Route
            path="/departments"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER]}>
                <DepartmentsPage />
              </RequireRole>
            }
          />
          <Route
            path="/departments/:id"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER]}>
                <DepartmentDetailPage />
              </RequireRole>
            }
          />
          <Route
            path="/designations"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER]}>
                <DesignationsPage />
              </RequireRole>
            }
          />
          <Route
            path="/reports"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER]}>
                <ReportsPage />
              </RequireRole>
            }
          />
          <Route
            path="/payments"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.HR_MANAGER, ROLES.EMPLOYEE]}>
                <PaymentsPage />
              </RequireRole>
            }
          />
        </Route>
      </Route>

      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Public website (no auth required) */}
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/cancellation-refund" element={<CancellationRefundPage />} />
      <Route path="/shipping-policy" element={<ShippingPolicyPage />} />

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
