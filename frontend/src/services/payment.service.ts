/**
 * Payment service.
 * API functions for office payment endpoints.
 */

import { http } from "./api";
import {
  Amenity,
  CreatePaymentPayload,
  Payment,
  PaymentListResponse,
  PaymentOrderResponse,
  VerifyPaymentPayload,
} from "@/types/payment";

export const paymentService = {
  async create(payload: CreatePaymentPayload): Promise<PaymentOrderResponse> {
    const response = await http.post<PaymentOrderResponse>("/payments/", payload);
    return response;
  },

  async list(params?: {
    employee_id?: string;
    department_id?: string;
    amenity_id?: string;
    status?: string;
    date?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaymentListResponse> {
    const response = await http.get<PaymentListResponse>("/payments/", { params });
    return response;
  },

  async verify(
    paymentId: string,
    payload: VerifyPaymentPayload
  ): Promise<Payment> {
    const response = await http.post<Payment>(
      `/payments/${paymentId}/verify/`,
      payload
    );
    return response;
  },

  async cancel(paymentId: string): Promise<Payment> {
    const response = await http.post<Payment>(`/payments/${paymentId}/cancel/`);
    return response;
  },

  async getMyPayments(params?: {
    status?: string;
    date?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaymentListResponse> {
    const response = await http.get<PaymentListResponse>("/payments/me/", {
      params,
    });
    return response;
  },

  async getAmenities(): Promise<Amenity[]> {
    const response = await http.get<{ amenities: Amenity[] }>(
      "/payments/amenities/"
    );
    return response.amenities;
  },
};
