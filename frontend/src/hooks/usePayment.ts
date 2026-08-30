/**
 * usePayment hook.
 * Provides convenient access to office payment state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  clearPayments,
  createPayment,
  fetchPayments,
  verifyPayment,
  cancelPayment,
  fetchMyPayments,
  fetchAmenities,
} from "@/store/slices/paymentSlice";
import { PaymentFilters } from "@/types/payment";

export function usePayment() {
  const dispatch = useDispatch<AppDispatch>();
  const {
    payments,
    amenities,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    amenitiesLoading,
    error,
  } = useSelector((state: RootState) => state.payment);

  const list = useCallback(
    (params?: PaymentFilters) => dispatch(fetchPayments(params || {})),
    [dispatch]
  );

  const create = useCallback(
    (payload: Parameters<typeof createPayment>[0]) =>
      dispatch(createPayment(payload)),
    [dispatch]
  );

  const verify = useCallback(
    (
      id: string,
      payload: Parameters<typeof verifyPayment>[0]["payload"]
    ) => dispatch(verifyPayment({ id, payload })),
    [dispatch]
  );

  const cancel = useCallback(
    (id: string) => dispatch(cancelPayment(id)),
    [dispatch]
  );

  const loadMyPayments = useCallback(
    (params?: {
      status?: string;
      date?: string;
      page?: number;
      page_size?: number;
    }) => dispatch(fetchMyPayments(params || {})),
    [dispatch]
  );

  const loadAmenities = useCallback(
    () => dispatch(fetchAmenities()),
    [dispatch]
  );

  return {
    payments,
    amenities,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    amenitiesLoading,
    error,
    list,
    create,
    verify,
    cancel,
    loadMyPayments,
    loadAmenities,
    clear: () => dispatch(clearPayments()),
  };
}
