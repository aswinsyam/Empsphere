/**
 * useDesignations hook.
 * Provides convenient access to designation state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  clearDesignations,
  createDesignation,
  fetchDesignations,
  updateDesignation,
} from "@/store/slices/designationSlice";
import { DesignationListParams } from "@/types/designation";

export function useDesignations() {
  const dispatch = useDispatch<AppDispatch>();
  const {
    designations,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    error,
  } = useSelector((state: RootState) => state.designation);

  const list = useCallback(
    (params?: DesignationListParams) =>
      dispatch(fetchDesignations(params || {})),
    [dispatch]
  );

  const create = useCallback(
    (payload: { name: string; code?: string; description?: string }) =>
      dispatch(createDesignation(payload)),
    [dispatch]
  );

  const update = useCallback(
    (id: string, payload: { name?: string; code?: string; description?: string; is_active?: boolean }) =>
      dispatch(updateDesignation({ id, ...payload })),
    [dispatch]
  );

  return {
    designations,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    error,
    list,
    create,
    update,
    clear: () => dispatch(clearDesignations()),
  };
}
