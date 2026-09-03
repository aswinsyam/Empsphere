/**
 * Generic API wrapper.
 * Provides typed helpers for GET/POST/PUT/PATCH/DELETE.
 * Unwraps the backend's `{success, message, data}` envelope automatically.
 */

import { api } from "@/config/axios";

interface BackendResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: unknown;
}

function unwrap<T>(payload: BackendResponse<T>): T {
  return payload.data;
}

export const http = {
  async get<T>(url: string, params?: unknown): Promise<T> {
    const res = await api.get<BackendResponse<T>>(url, { params });
    return unwrap<T>(res.data);
  },

  async post<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.post<BackendResponse<T>>(url, data);
    return unwrap<T>(res.data);
  },

  async put<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.put<BackendResponse<T>>(url, data);
    return unwrap<T>(res.data);
  },

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const res = await api.patch<BackendResponse<T>>(url, data);
    return unwrap<T>(res.data);
  },

  async delete<T>(url: string): Promise<T> {
    const res = await api.delete<BackendResponse<T>>(url);
    return unwrap<T>(res.data);
  },
};
