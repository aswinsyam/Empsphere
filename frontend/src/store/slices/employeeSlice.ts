/**
 * Employee slice.
 * Manages employee list state with Redux Toolkit.
 *
 * Employee Management exposes fetch / create / update only. There is no
 * delete thunk because employee deletion is not part of the module UI.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { employeeService } from "@/services/employee.service";
import {
  CreateEmployeePayload,
  Employee,
  EmployeeListParams,
  UpdateEmployeePayload,
} from "@/types/employee";

interface EmployeeState {
  employees: Employee[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
  loading: boolean;
  error: string | null;
}

const initialState: EmployeeState = {
  employees: [],
  total_records: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
  loading: false,
  error: null,
};

export const fetchEmployees = createAsyncThunk<
  { employees: Employee[]; total_records: number; total_pages: number; page: number; page_size: number },
  EmployeeListParams
>("employee/fetchAll", async (params) => {
  const res = await employeeService.list(params);
  return {
    employees: res.employees,
    total_records: res.total_records,
    total_pages: res.total_pages,
    page: res.page,
    page_size: res.page_size,
  };
});

export const createEmployee = createAsyncThunk<
  { user_id: string },
  CreateEmployeePayload
>("employee/create", async (payload) => {
  return employeeService.create(payload);
});

export const updateEmployee = createAsyncThunk<
  Employee,
  { id: string; payload: UpdateEmployeePayload }
>("employee/update", async ({ id, payload }) => {
  return employeeService.update(id, payload);
});

const employeeSlice = createSlice({
  name: "employee",
  initialState,
  reducers: {
    clearEmployees(state) {
      state.employees = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // fetch all
    builder.addCase(fetchEmployees.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(
      fetchEmployees.fulfilled,
      (state, action: PayloadAction<{ employees: Employee[]; total_records: number; total_pages: number; page: number; page_size: number }>) => {
        state.loading = false;
        state.employees = action.payload.employees;
        state.total_records = action.payload.total_records;
        state.total_pages = action.payload.total_pages;
        state.page = action.payload.page;
        state.page_size = action.payload.page_size;
      }
    );
    builder.addCase(fetchEmployees.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to load employees.";
    });

    // create
    builder.addCase(createEmployee.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createEmployee.fulfilled, (state) => {
      state.loading = false;
    });
    builder.addCase(createEmployee.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to create employee.";
    });

    // update
    builder.addCase(updateEmployee.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateEmployee.fulfilled, (state, action: PayloadAction<Employee>) => {
      state.loading = false;
      const idx = state.employees.findIndex((e) => e.user_id === action.payload.user_id);
      if (idx >= 0) {
        state.employees[idx] = action.payload;
      }
    });
    builder.addCase(updateEmployee.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to update employee.";
    });
  },
});

export const { clearEmployees } = employeeSlice.actions;

export default employeeSlice.reducer;
