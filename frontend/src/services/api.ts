/**
 * Generic API wrapper.
 * Provides typed helpers for GET/POST/PUT/PATCH/DELETE.
 */

import { api } from "@/config/axios";
import { ApiResponse } from "@/types/api";

export const http = {
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const res = await api.get<ApiResponse<T>>(url, { params });
    return res.data.data;
  },

  async post<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.post<ApiResponse<T>>(url, data);
    return res.data.data;
  },

  async put<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.put<ApiResponse<T>>(url, data);
    return res.data.data;
  },

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.patch<ApiResponse<T>>(url, data);
    return res.data.data;
  },

  async delete<T>(url: string): Promise<T> {
    const res = await api.delete<ApiResponse<T>>(url);
    return res.data.data;
  },
};
