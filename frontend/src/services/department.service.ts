/**
 * Department API service.
 * Calls the backend organization department endpoints.
 */

import { http } from "./api";
import {
  CreateDepartmentPayload,
  Department,
  UpdateDepartmentPayload,
} from "@/types/department";

export const departmentService = {
  /** List all departments. */
  async list(): Promise<Department[]> {
    return http.get<Department[]>("/organization/departments/");
  },

  /** Get a single department by id. */
  async getById(id: string): Promise<Department> {
    return http.get<Department>(`/organization/departments/${id}/`);
  },

  /** Create a department. */
  async create(payload: CreateDepartmentPayload): Promise<Department> {
    return http.post<Department>("/organization/departments/", payload);
  },

  /** Update a department. */
  async update(
    id: string,
    payload: UpdateDepartmentPayload
  ): Promise<Department> {
    return http.put<Department>(`/organization/departments/${id}/`, payload);
  },

  /** Delete (soft) a department. */
  async remove(id: string): Promise<null> {
    return http.delete<null>(`/organization/departments/${id}/`);
  },
};
