/**
 * Department slice.
 * Manages department list state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { departmentService } from "@/services/department.service";
import {
  CreateDepartmentPayload,
  Department,
  UpdateDepartmentPayload,
} from "@/types/department";

interface DepartmentState {
  departments: Department[];
  loading: boolean;
  error: string | null;
}

const initialState: DepartmentState = {
  departments: [],
  loading: false,
  error: null,
};

/** Fetch all departments. */
export const fetchDepartments = createAsyncThunk<Department[], void>(
  "department/fetchAll",
  async () => {
    return departmentService.list();
  }
);

/** Create a department. */
export const createDepartment = createAsyncThunk<
  Department,
  CreateDepartmentPayload
>("department/create", async (payload) => {
  return departmentService.create(payload);
});

/** Update a department. */
export const updateDepartment = createAsyncThunk<
  Department,
  { id: string; payload: UpdateDepartmentPayload }
>("department/update", async ({ id, payload }) => {
  return departmentService.update(id, payload);
});

/** Delete a department. */
export const deleteDepartment = createAsyncThunk<string, string>(
  "department/delete",
  async (id) => {
    await departmentService.remove(id);
    return id;
  }
);

const departmentSlice = createSlice({
  name: "department",
  initialState,
  reducers: {
    clearDepartments(state) {
      state.departments = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // fetch all
    builder.addCase(fetchDepartments.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(
      fetchDepartments.fulfilled,
      (state, action: PayloadAction<Department[]>) => {
        state.loading = false;
        state.departments = action.payload;
      }
    );
    builder.addCase(fetchDepartments.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to load departments.";
    });

    // create
    builder.addCase(createDepartment.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createDepartment.fulfilled, (state) => {
      state.loading = false;
    });
    builder.addCase(createDepartment.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to create department.";
    });

    // update
    builder.addCase(updateDepartment.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateDepartment.fulfilled, (state) => {
      state.loading = false;
    });
    builder.addCase(updateDepartment.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to update department.";
    });

    // delete
    builder.addCase(deleteDepartment.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(deleteDepartment.fulfilled, (state, action) => {
      state.loading = false;
      state.departments = state.departments.filter(
        (d) => d.department_id !== action.payload
      );
    });
    builder.addCase(deleteDepartment.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || "Failed to delete department.";
    });
  },
});

export const { clearDepartments } = departmentSlice.actions;

export default departmentSlice.reducer;
