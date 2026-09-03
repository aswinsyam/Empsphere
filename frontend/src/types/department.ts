/**
 * Department-related types.
 * Mirrors the backend department document and API payloads.
 */

/** Department document returned by the backend. */
export interface Department {
  department_id: string;
  name: string;
  code: string;
  description?: string | null;
  head_user_id?: string | null;
  organization_id?: string | null;
  is_active?: boolean;
  employee_count?: number;
  created_at?: string;
  updated_at?: string;
}

/** Payload for creating a department. */
export interface CreateDepartmentPayload {
  name: string;
  code: string;
  description?: string;
  head_user_id?: string | null;
  organization_id?: string | null;
}

/** Payload for updating a department. */
export interface UpdateDepartmentPayload {
  name?: string;
  code?: string;
  description?: string | null;
  head_user_id?: string | null;
  organization_id?: string | null;
  is_active?: boolean;
}

/** Paginated department list response. */
export interface DepartmentListResponse {
  departments: Department[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/** List params for departments. */
export interface DepartmentListParams {
  search?: string;
  page?: number;
  page_size?: number;
  include_inactive?: boolean;
}
