/**
 * Attendance API service.
 * Calls the backend attendance endpoints.
 */

import { http } from "./api";
import {
  AttendanceListResponse,
  AttendanceRecord,
  AttendanceSummary,
} from "@/types/attendance";

/** Client for attendance endpoints. */
export const attendanceService = {
  /** List attendance records with optional filters. */
  async list(params?: {
    employee_id?: string;
    start_date?: string;
    end_date?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<AttendanceListResponse> {
    return http.get<AttendanceListResponse>("/attendance/", params);
  },

  /** Mark attendance for an employee. */
  async mark(payload: {
    employee_id?: string;
    date: string;
    status?: string;
    check_in?: string;
    check_out?: string;
    remarks?: string;
  }): Promise<{ attendance_id: string }> {
    return http.post<{ attendance_id: string }>("/attendance/", payload);
  },

  /** Update attendance. */
  async update(
    id: string,
    payload: {
      status?: string;
      check_in?: string;
      check_out?: string;
      remarks?: string;
    }
  ): Promise<AttendanceRecord> {
    return http.put<AttendanceRecord>(`/attendance/${id}/`, payload);
  },

  /** Get attendance summary for an employee. */
  async summary(employee_id: string, start_date?: string, end_date?: string): Promise<AttendanceSummary> {
    return http.get<AttendanceSummary>(`/attendance/summary/${employee_id}/`, {
      params: { start_date, end_date },
    });
  },

  /** Check in for today. */
  async checkIn(): Promise<AttendanceRecord> {
    return http.post<AttendanceRecord>("/attendance/actions/check-in/", {});
  },

  /** Check out for today. */
  async checkOut(): Promise<AttendanceRecord> {
    return http.post<AttendanceRecord>("/attendance/actions/check-out/", {});
  },
};
