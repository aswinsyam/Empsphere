/**
 * User/employee related types.
 */

/** User profile returned by /me/ endpoint. */
export interface UserProfile {
  _id: string;
  employee_code?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email: string;
  phone?: string;
  role: string;
  department_id?: string | null;
  designation_id?: string | null;
  profile_image_id?: string;
  login_provider?: string;
  is_email_verified?: boolean;
  is_active?: boolean;
  last_login?: string | null;
  created_at?: string;
  updated_at?: string;
}
