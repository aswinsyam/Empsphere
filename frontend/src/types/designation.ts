/**
 * Designation related types.
 */

/** Designation record returned by the backend. */
export interface Designation {
  designation_id: string;
  name: string;
  code?: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/** Paginated designation response. */
export interface DesignationListResponse {
  designations: Designation[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/** Designation list params. */
export interface DesignationListParams {
  search?: string;
  page?: number;
  page_size?: number;
  include_inactive?: boolean;
}
