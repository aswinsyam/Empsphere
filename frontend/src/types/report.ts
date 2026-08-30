/**
 * Report-related types.
 */

/** Unified report response envelope. */
export interface ReportResponse {
  summary: Record<string, unknown>;
  records: Record<string, unknown>[];
  meta: {
    page: number;
    page_size: number;
    total_records: number;
    total_pages: number;
  };
}
