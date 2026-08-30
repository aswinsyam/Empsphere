/**
 * Shared API types.
 */

/** Standard success response envelope returned by the backend. */
export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  meta?: {
    page: number;
    page_size: number;
    total_records: number;
    total_pages: number;
  } | null;
}
