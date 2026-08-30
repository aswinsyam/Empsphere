/**
 * useAttendance hook.
 * Provides convenient access to attendance state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  clearAttendance,
  fetchAttendance,
  fetchAttendanceSummary,
  markAttendance,
  updateAttendance,
  checkIn as checkInAction,
  checkOut as checkOutAction,
} from "@/store/slices/attendanceSlice";

export function useAttendance() {
  const dispatch = useDispatch<AppDispatch>();
  const { records, summary, loading, error, page, page_size, total_records, total_pages } = useSelector(
    (state: RootState) => state.attendance
  );

  const list = useCallback(
    (params?: { employee_id?: string; start_date?: string; end_date?: string; status?: string; page?: number; page_size?: number }) =>
      dispatch(fetchAttendance(params || {})),
    [dispatch]
  );

  const mark = useCallback(
    (payload: { employee_id?: string; date: string; status?: string; check_in?: string; check_out?: string; remarks?: string }) =>
      dispatch(markAttendance(payload)),
    [dispatch]
  );

  const update = useCallback(
    (id: string, payload: { status?: string; check_in?: string; check_out?: string; remarks?: string }) =>
      dispatch(updateAttendance({ id, ...payload })),
    [dispatch]
  );

  const loadSummary = useCallback(
    (params: { employee_id: string; start_date?: string; end_date?: string }) =>
      dispatch(fetchAttendanceSummary(params)),
    [dispatch]
  );

  const checkIn = useCallback(
    () => dispatch(checkInAction()),
    [dispatch]
  );

  const checkOut = useCallback(
    () => dispatch(checkOutAction()),
    [dispatch]
  );

  return {
    records,
    summary,
    loading,
    error,
    page,
    page_size,
    total_records,
    total_pages,
    list,
    mark,
    update,
    loadSummary,
    checkIn,
    checkOut,
    clear: () => dispatch(clearAttendance()),
  };
}
