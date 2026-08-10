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
