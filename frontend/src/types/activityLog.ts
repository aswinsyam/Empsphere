/**
 * Activity log related types.
 */

/** Activity log entry returned by the backend. */
export interface ActivityLog {
  log_id: string;
  module: string;
  action: string;
  performed_by: string;
  target_id?: string;
  status: string;
  description: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

/** Paginated activity log response (unwrapped from ApiResponse.data). */
export interface ActivityLogListResponse {
  logs: ActivityLog[];
  meta: {
    page: number;
    page_size: number;
    total_records: number;
    total_pages: number;
  };
}
