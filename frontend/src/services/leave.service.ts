/**
 * Leave API service.
 * Calls the backend leave endpoints.
 */

import { http } from "./api";
import { LeaveListResponse, LeaveRecord } from "@/types/leave";

/** Client for leave endpoints. */
export const leaveService = {
  /** List leaves with optional filters. */
  async list(params?: {
    employee_id?: string;
    status?: string;
    leave_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<LeaveListResponse> {
    return http.get<LeaveListResponse>("/leaves/", params);
  },

  /** Get a single leave by id. */
  async getById(id: string): Promise<LeaveRecord> {
    return http.get<LeaveRecord>(`/leaves/${id}/`);
  },

  /** Apply for leave. */
  async apply(payload: {
    employee_id: string;
    start_date: string;
    end_date: string;
    leave_type?: string;
    reason?: string;
  }): Promise<{ leave_id: string }> {
    return http.post<{ leave_id: string }>("/leaves/", payload);
  },

  /** Approve or reject leave. */
  async updateStatus(
    id: string,
    status: "APPROVED" | "REJECTED"
  ): Promise<LeaveRecord> {
    return http.put<LeaveRecord>(`/leaves/${id}/`, { status });
  },
};
