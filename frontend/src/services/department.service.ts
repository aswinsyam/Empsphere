/**
 * Department API service.
 * Calls the backend organization department endpoints.
 */

import { http } from "./api";
import {
  CreateDepartmentPayload,
  Department,
  DepartmentListResponse,
  UpdateDepartmentPayload,
} from "@/types/department";

/** Client for organization department endpoints. */
export const departmentService = {
  /** List departments with optional search and pagination. */
   async list(params?: {
    search?: string;
    page?: number;
    page_size?: number;
    include_inactive?: boolean;
  }): Promise<DepartmentListResponse> {
    return http.get<DepartmentListResponse>("/departments/", params);
  },

  /** Get a single department by id. */
  async getById(id: string): Promise<Department> {
    return http.get<Department>(`/departments/${id}/`);
  },

  /** Create a department. */
  async create(payload: CreateDepartmentPayload): Promise<Department> {
    return http.post<Department>("/departments/", payload);
  },

  /** Update a department. */
  async update(
    id: string,
    payload: UpdateDepartmentPayload
  ): Promise<Department> {
    return http.put<Department>(`/departments/${id}/`, payload);
  },

  /** Delete (soft) a department. */
  async remove(id: string): Promise<null> {
    return http.delete<null>(`/departments/${id}/`);
  },
};
