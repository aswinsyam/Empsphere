/**
 * Statistics API service.
 */

import { http } from "./api";

export interface DashboardStatistics {
  total_employees: number;
  total_departments: number;
  total_attendance: number;
  pending_leaves: number;
}

export const statisticsService = {
  async getDashboardStats(): Promise<DashboardStatistics> {
    return http.get<DashboardStatistics>("/statistics/");
  },
};
