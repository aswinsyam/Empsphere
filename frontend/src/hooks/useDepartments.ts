/**
 * useDepartments hook.
 * Provides convenient access to department state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  createDepartment,
  deleteDepartment,
  fetchDepartments,
  updateDepartment,
} from "@/store/slices/departmentSlice";
import {
  CreateDepartmentPayload,
  UpdateDepartmentPayload,
} from "@/types/department";

export function useDepartments() {
  const dispatch = useDispatch<AppDispatch>();
  const { departments, total_records, total_pages, page, page_size, loading, error } = useSelector(
    (state: RootState) => state.department
  );

  const list = useCallback(
    (params?: { search?: string; page?: number; page_size?: number; include_inactive?: boolean }) =>
      dispatch(fetchDepartments(params || {})),
    [dispatch]
  );

  const create = useCallback(
    (payload: CreateDepartmentPayload) => dispatch(createDepartment(payload)),
    [dispatch]
  );

  const update = useCallback(
    (id: string, payload: UpdateDepartmentPayload) =>
      dispatch(updateDepartment({ id, payload })),
    [dispatch]
  );

  const remove = useCallback(
    (id: string) => dispatch(deleteDepartment(id)),
    [dispatch]
  );

  return { departments, total_records, total_pages, page, page_size, loading, error, list, create, update, remove };
}
