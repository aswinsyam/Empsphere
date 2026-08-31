/**
 * Payment related types for office payment module.
 */

export type PaymentStatus = "PENDING" | "PAID" | "FAILED" | "CANCELLED";

/** Amenity record returned by the backend. */
export interface Amenity {
  amenity_id: string;
  name: string;
  description: string;
  amount: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/** Payment record returned by the backend. */
export interface Payment {
  payment_id: string;
  employee_id: string;
  paid_by: string;
  amenity_id: string;
  amenity_name: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  gateway: string;
  gateway_order_id?: string;
  gateway_payment_id?: string;
  payment_date?: string;
  created_at?: string;
  updated_at?: string;
}

/** Payment filters for list requests. */
export interface PaymentFilters {
  employee_id?: string;
  department_id?: string;
  amenity_id?: string;
  status?: string;
  date?: string;
  page?: number;
  page_size?: number;
}

/** Paginated payment response. */
export interface PaymentListResponse {
  payments: Payment[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/** Payment creation payload. */
export interface CreatePaymentPayload {
  employee_id?: string;
  amenity_id: string;
}

/** Payment verification payload. */
export interface VerifyPaymentPayload {
  gateway_order_id: string;
  gateway_payment_id: string;
  payment_status?: string;
}

/** Payment order response from backend. */
export interface PaymentOrderResponse {
  payment_id: string;
  order_id: string;
  payment_session_id: string;
  amount: number;
  currency: string;
}
