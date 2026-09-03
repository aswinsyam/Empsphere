/**
 * Employee API service.
 * Calls the backend employee endpoints.
 *
 * Employee Management is view / create / edit only, so no delete call is
 * exposed here. The backend DELETE endpoint remains SUPER_ADMIN-only and is
 * intentionally left untouched.
 */

import { http } from "./api";
import {
  CreateEmployeePayload,
  Employee,
  EmployeeListParams,
  EmployeeListResponse,
  UpdateEmployeePayload,
} from "@/types/employee";

/** Client for employee endpoints. */
export const employeeService = {
  /** List employees with optional filters. */
  async list(params?: EmployeeListParams): Promise<EmployeeListResponse> {
    return http.get<EmployeeListResponse>("/employees/", params);
  },

  /** Get a single employee by id. */
  async getById(id: string): Promise<Employee> {
    return http.get<Employee>(`/employees/${id}/`);
  },

  /** Create an employee. */
  async create(payload: CreateEmployeePayload): Promise<{ user_id: string }> {
    return http.post<{ user_id: string }>("/employees/", payload);
  },

  /** Update an employee. */
  async update(
    id: string,
    payload: UpdateEmployeePayload
  ): Promise<Employee> {
    return http.put<Employee>(`/employees/${id}/`, payload);
  },
};
