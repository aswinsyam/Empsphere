/**
 * Leave related types.
 */

/** Leave record returned by the backend. */
export interface LeaveRecord {
  leave_id: string;
  employee_id: string;
  employee_name?: string;
  employee_code?: string;
  email?: string;
  start_date: string;
  end_date: string;
  leave_type: string;
  reason?: string;
  status: string;
  approved_by?: string;
  rejected_by?: string;
  created_at?: string;
  updated_at?: string;
}

/** Paginated leave response. */
export interface LeaveListResponse {
  leaves: LeaveRecord[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}
