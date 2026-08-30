/**
 * Payment slice.
 * Manages office payment list state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { paymentService } from "@/services/payment.service";
import {
  Amenity,
  CreatePaymentPayload,
  Payment,
  PaymentListResponse,
  PaymentOrderResponse,
  VerifyPaymentPayload,
} from "@/types/payment";

interface PaymentState {
  payments: Payment[];
  amenities: Amenity[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
  loading: boolean;
  amenitiesLoading: boolean;
  error: string | null;
}

const initialState: PaymentState = {
  payments: [],
  amenities: [],
  total_records: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
  loading: false,
  amenitiesLoading: false,
  error: null,
};

export const fetchPayments = createAsyncThunk<
  PaymentListResponse,
  {
    employee_id?: string;
    department_id?: string;
    amenity_id?: string;
    status?: string;
    date?: string;
    page?: number;
    page_size?: number;
  }
>("payment/fetchAll", async (params) => {
  const res = await paymentService.list(params);
  return res;
});

export const createPayment = createAsyncThunk<
  PaymentOrderResponse,
  CreatePaymentPayload
>("payment/create", async (payload) => {
  return paymentService.create(payload);
});

export const verifyPayment = createAsyncThunk<
  Payment,
  { id: string; payload: VerifyPaymentPayload }
>("payment/verify", async ({ id, payload }) => {
  const res = await paymentService.verify(id, payload);
  return res;
});

export const cancelPayment = createAsyncThunk<Payment, string>(
  "payment/cancel",
  async (paymentId) => {
    const res = await paymentService.cancel(paymentId);
    return res;
  }
);

export const fetchMyPayments = createAsyncThunk<
  PaymentListResponse,
  {
    status?: string;
    date?: string;
    page?: number;
    page_size?: number;
  }
>("payment/fetchMy", async (params) => {
  return paymentService.getMyPayments(params);
});

export const fetchAmenities = createAsyncThunk<Amenity[]>(
  "payment/fetchAmenities",
  async () => {
    return paymentService.getAmenities();
  }
);

const paymentSlice = createSlice({
  name: "payment",
  initialState,
  reducers: {
    clearPayments(state) {
      state.payments = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPayments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchPayments.fulfilled,
        (state, action: PayloadAction<PaymentListResponse>) => {
          state.loading = false;
          state.payments = action.payload.payments;
          state.total_records = action.payload.total_records;
          state.total_pages = action.payload.total_pages;
          state.page = action.payload.page;
          state.page_size = action.payload.page_size;
        }
      )
      .addCase(fetchPayments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load payments.";
      })
      .addCase(createPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to create payment.";
      })
      .addCase(verifyPayment.fulfilled, (state, action: PayloadAction<Payment>) => {
        state.loading = false;
        const idx = state.payments.findIndex(
          (p) => p.payment_id === action.payload.payment_id
        );
        if (idx >= 0) {
          state.payments[idx] = action.payload;
        }
      })
      .addCase(verifyPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to verify payment.";
      })
      .addCase(cancelPayment.fulfilled, (state, action: PayloadAction<Payment>) => {
        state.loading = false;
        const idx = state.payments.findIndex(
          (p) => p.payment_id === action.payload.payment_id
        );
        if (idx >= 0) {
          state.payments[idx] = action.payload;
        }
      })
      .addCase(cancelPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to cancel payment.";
      })
      .addCase(fetchMyPayments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchMyPayments.fulfilled,
        (state, action: PayloadAction<PaymentListResponse>) => {
          state.loading = false;
          state.payments = action.payload.payments;
          state.total_records = action.payload.total_records;
          state.total_pages = action.payload.total_pages;
          state.page = action.payload.page;
          state.page_size = action.payload.page_size;
        }
      )
      .addCase(fetchMyPayments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load payments.";
      })
      .addCase(fetchAmenities.pending, (state) => {
        state.amenitiesLoading = true;
      })
      .addCase(
        fetchAmenities.fulfilled,
        (state, action: PayloadAction<Amenity[]>) => {
          state.amenitiesLoading = false;
          state.amenities = action.payload;
        }
      )
      .addCase(fetchAmenities.rejected, (state) => {
        state.amenitiesLoading = false;
      });
  },
});

export const { clearPayments } = paymentSlice.actions;
export default paymentSlice.reducer;
