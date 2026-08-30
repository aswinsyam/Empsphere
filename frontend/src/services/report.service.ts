/**
 * Report API service.
 * Calls the backend report endpoints.
 */

import { http } from "./api";
import { ReportResponse } from "@/types/report";

/** Client for report endpoints. */
export const reportService = {
  /** Generate employee report. */
  async getEmployeeReport(params?: {
    search?: string;
    department_id?: string;
    designation_id?: string;
    status?: string;
    joining_date_from?: string;
    joining_date_to?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/employees/", params);
  },

  /** Generate attendance report. */
  async getAttendanceReport(params?: {
    employee_id?: string;
    department_id?: string;
    start_date?: string;
    end_date?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/attendance/", params);
  },

  /** Generate leave report. */
  async getLeaveReport(params?: {
    employee_id?: string;
    department_id?: string;
    start_date?: string;
    end_date?: string;
    status?: string;
    leave_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/leaves/", params);
  },

  /** Generate department report. */
  async getDepartmentReport(params?: {
    search?: string;
    include_inactive?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/departments/", params);
  },

  /** Generate designation report. */
  async getDesignationReport(params?: {
    search?: string;
    include_inactive?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/designations/", params);
  },

  /** Generate activity report. */
  async getActivityReport(params?: {
    module?: string;
    action?: string;
    user_id?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReportResponse> {
    return http.get<ReportResponse>("/reports/activity/", params);
  },
};
