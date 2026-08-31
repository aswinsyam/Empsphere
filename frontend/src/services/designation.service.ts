/**
 * Designation API service.
 * Calls the backend designation endpoints.
 */

import { http } from "./api";
import { Designation, DesignationListResponse } from "@/types/designation";

/** Client for designation endpoints. */
export const designationService = {
  /** List designations with optional search and pagination. */
  async list(params?: {
    search?: string;
    page?: number;
    page_size?: number;
    include_inactive?: boolean;
  }): Promise<DesignationListResponse> {
    return http.get<DesignationListResponse>("/organization/designations/", params);
  },

  /** Create a new designation. */
  async create(payload: {
    name: string;
    code?: string;
    description?: string;
  }): Promise<Designation> {
    return http.post<Designation>("/organization/designations/", payload);
  },

  /** Update a designation. */
  async update(
    id: string,
    payload: {
      name?: string;
      code?: string;
      description?: string;
      is_active?: boolean;
    }
  ): Promise<Designation> {
    return http.put<Designation>(`/organization/designations/${id}/`, payload);
  },
};
