/**
 * Attendance related types.
 */

/** Attendance record returned by the backend. */
export interface AttendanceRecord {
  attendance_id: string;
  employee_id: string;
  date: string;
  status: string;
  check_in?: string;
  check_out?: string;
  remarks?: string;
  created_at?: string;
  updated_at?: string;
}

/** Paginated attendance response. */
export interface AttendanceListResponse {
  attendance: AttendanceRecord[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/** Attendance summary response. */
export interface AttendanceSummary {
  total_days: number;
  present_days: number;
  absent_days: number;
  half_days: number;
  leave_days: number;
  attendance_percentage: number;
}
