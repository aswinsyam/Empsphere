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

/** Standard error response envelope returned by the backend. */
export interface ApiErrorResponse {
  success: boolean;
  message: string;
  errors?: Record<string, unknown> | null;
}

/** Pagination metadata. */
export interface PaginationMeta {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}
