/**
 * Employee-related types.
 */

/** Employee document returned by the backend. */
export interface Employee {
  user_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  email: string;
  phone?: string;
  role: string;
  department_id?: string | null;
  designation_id?: string | null;
  profile_image_id?: string;
  is_email_verified?: boolean;
  login_provider?: string;
  last_login?: string | null;
  is_active?: boolean;
  status?: string;
  joining_date?: string;
  created_at?: string;
  updated_at?: string;
  working_duration?: string | null;
  total_working_days?: number | null;
}

/** Payload for creating an employee. */
export interface CreateEmployeePayload {
  first_name: string;
  last_name: string;
  email: string;
  password?: string;
  phone?: string;
  role?: string;
  department_id?: string | null;
  designation_id?: string | null;
  joining_date?: string;
  status?: string;
}

/** Payload for updating an employee. */
export interface UpdateEmployeePayload {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  role?: string;
  department_id?: string | null;
  designation_id?: string | null;
  joining_date?: string;
  status?: string;
}

/** Paginated employee list response. */
export interface EmployeeListResponse {
  employees: Employee[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/** List params for employees. */
export interface EmployeeListParams {
  search?: string;
  department_id?: string;
  status?: string;
  joining_date_from?: string;
  joining_date_to?: string;
  page?: number;
  page_size?: number;
}
