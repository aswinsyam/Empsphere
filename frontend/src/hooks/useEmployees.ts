/**
 * useEmployees hook.
 * Provides convenient access to employee state and actions.
 *
 * Employee deletion is intentionally not exposed: Employee Management
 * supports view / create / edit and status activate-deactivate only.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  clearEmployees,
  createEmployee,
  fetchEmployees,
  updateEmployee,
} from "@/store/slices/employeeSlice";
import {
  CreateEmployeePayload,
  EmployeeListParams,
  UpdateEmployeePayload,
} from "@/types/employee";

export function useEmployees() {
  const dispatch = useDispatch<AppDispatch>();
  const { employees, total_records, total_pages, page, page_size, loading, error } = useSelector(
    (state: RootState) => state.employee
  );

  const list = useCallback(
    (params?: EmployeeListParams) =>
      dispatch(fetchEmployees(params || {})),
    [dispatch]
  );

  const create = useCallback(
    (payload: CreateEmployeePayload) => dispatch(createEmployee(payload)),
    [dispatch]
  );

  const update = useCallback(
    (id: string, payload: UpdateEmployeePayload) =>
      dispatch(updateEmployee({ id, payload })),
    [dispatch]
  );

  return {
    employees,
    total_records,
    total_pages,
    page,
    page_size,
    loading,
    error,
    list,
    create,
    update,
    clear: () => dispatch(clearEmployees()),
  };
}
