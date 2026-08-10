/**
 * AppRoutes.
 * Central route configuration for the application.
 */

import { Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./ProtectedRoute";
import { RequireRole } from "./RequireRole";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { ForgotPasswordPage } from "@/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/auth/ResetPasswordPage";
import { VerifyEmailPage } from "@/pages/auth/VerifyEmailPage";
import { ChangePasswordPage } from "@/pages/auth/ChangePasswordPage";
import { SetPasswordPage } from "@/pages/auth/SetPasswordPage";
import { ProfilePage } from "@/pages/profile/ProfilePage";
import { DashboardRedirect } from "./DashboardRedirect";
import { SuperAdminDashboardPage } from "@/pages/dashboard/SuperAdminDashboardPage";
import { AdminDashboardPage } from "@/pages/dashboard/AdminDashboardPage";
import { HRDashboardPage } from "@/pages/dashboard/HRDashboardPage";
import { EmployeeDashboardPage } from "@/pages/dashboard/EmployeeDashboardPage";
import { DepartmentsPage } from "@/pages/departments/DepartmentsPage";
import { CreateUserPage } from "@/pages/users/CreateUserPage";
import { NotFoundPage } from "@/pages/errors/NotFoundPage";
import { UnauthorizedPage } from "@/pages/errors/UnauthorizedPage";
import { ROLES } from "@/utils/constants";

export function AppRoutes() {
  return (
    <Routes>
      {/* Public/auth routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<DashboardRedirect />} />
          <Route
            path="/dashboard/super-admin"
            element={
              <RequireRole roles={[ROLES.SUPER_ADMIN]}>
                <SuperAdminDashboardPage />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/admin"
            element={
              <RequireRole roles={[ROLES.ADMIN]}>
                <AdminDashboardPage />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/hr"
            element={
              <RequireRole roles={[ROLES.HR_MANAGER]}>
                <HRDashboardPage />
              </RequireRole>
            }
          />
          <Route
            path="/dashboard/employee"
            element={
              <RequireRole roles={[ROLES.EMPLOYEE]}>
                <EmployeeDashboardPage />
              </RequireRole>
            }
          />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/set-password" element={<SetPasswordPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/departments" element={<DepartmentsPage />} />
          <Route path="/users/create" element={<CreateUserPage />} />
        </Route>
      </Route>

      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
