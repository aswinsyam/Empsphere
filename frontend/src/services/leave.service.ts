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

  /**
   * Approve or reject leave.
   * The backend requires a non-empty reason for both decisions.
   */
  async updateStatus(
    id: string,
    status: "APPROVED" | "REJECTED",
    reason: string
  ): Promise<LeaveRecord> {
    const payload: Record<string, string> = { status };
    if (status === "APPROVED") {
      payload.approval_reason = reason;
    } else {
      payload.rejection_reason = reason;
    }
    return http.put<LeaveRecord>(`/leaves/${id}/`, payload);
  },
};