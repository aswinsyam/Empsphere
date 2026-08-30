/**
 * useLeave hook.
 * Provides convenient access to leave state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  applyLeave,
  clearLeaves,
  fetchLeaves,
  updateLeaveStatus,
} from "@/store/slices/leaveSlice";

export function useLeaves() {
  const dispatch = useDispatch<AppDispatch>();
  const { leaves, total_records, total_pages, page, page_size, loading, error } = useSelector(
    (state: RootState) => state.leave
  );

  const list = useCallback(
    (params?: { employee_id?: string; status?: string; leave_type?: string; start_date?: string; end_date?: string; page?: number; page_size?: number }) =>
      dispatch(fetchLeaves(params || {})),
    [dispatch]
  );

  const apply = useCallback(
    (payload: { employee_id: string; start_date: string; end_date: string; leave_type?: string; reason?: string }) =>
      dispatch(applyLeave(payload)),
    [dispatch]
  );

  const updateStatus = useCallback(
    (id: string, status: "APPROVED" | "REJECTED") =>
      dispatch(updateLeaveStatus({ id, status })),
    [dispatch]
  );

  return {
    leaves,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    error,
    list,
    apply,
    updateStatus,
    clear: () => dispatch(clearLeaves()),
  };
}
