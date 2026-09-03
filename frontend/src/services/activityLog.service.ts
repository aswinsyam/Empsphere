/**
 * Activity log API service.
 * Calls the backend activity log endpoints.
 */

import { http } from "./api";
import { ActivityLogListResponse } from "@/types/activityLog";

/** Client for activity log endpoints. */
export const activityLogService = {
  /** List activity logs with optional filters. */
  async list(params?: {
    module?: string;
    action?: string;
    user_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<ActivityLogListResponse> {
    return http.get<ActivityLogListResponse>("/activity-logs/", params);
  },

  /** Get distinct action values. */
  async distinctActions(): Promise<string[]> {
    const res = await http.get<{ actions: string[] }>("/activity-logs/actions/");
    return res.actions;
  },
};
