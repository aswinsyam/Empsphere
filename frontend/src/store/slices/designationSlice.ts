/**
 * Designation slice.
 * Manages designation state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { designationService } from "@/services/designation.service";
import { Designation, DesignationListResponse } from "@/types/designation";

interface DesignationState {
  designations: Designation[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
  loading: boolean;
  error: string | null;
}

const initialState: DesignationState = {
  designations: [],
  total_records: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
  loading: false,
  error: null,
};

export const fetchDesignations = createAsyncThunk<
  DesignationListResponse,
  { search?: string; page?: number; page_size?: number; include_inactive?: boolean }
>("designation/fetchAll", async (params) => {
  const res = await designationService.list(params);
  return res;
});

export const createDesignation = createAsyncThunk<
  Designation,
  { name: string; code?: string; description?: string }
>("designation/create", async (payload) => {
  return designationService.create(payload);
});

export const updateDesignation = createAsyncThunk<
  Designation,
  { id: string; name?: string; code?: string; description?: string; is_active?: boolean }
>("designation/update", async ({ id, ...payload }) => {
  return designationService.update(id, payload);
});

const designationSlice = createSlice({
  name: "designation",
  initialState,
  reducers: {
    clearDesignations(state) {
      state.designations = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDesignations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchDesignations.fulfilled,
        (state, action: PayloadAction<DesignationListResponse>) => {
          state.loading = false;
          state.designations = action.payload.designations;
          state.total_records = action.payload.total_records;
          state.total_pages = action.payload.total_pages;
          state.page = action.payload.page;
          state.page_size = action.payload.page_size;
        }
      )
      .addCase(fetchDesignations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load designations.";
      })
      .addCase(createDesignation.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createDesignation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to create designation.";
      })
      .addCase(updateDesignation.fulfilled, (state, action: PayloadAction<Designation>) => {
        state.loading = false;
        const idx = state.designations.findIndex((d) => d.designation_id === action.payload.designation_id);
        if (idx >= 0) {
          state.designations[idx] = action.payload;
        }
      })
      .addCase(updateDesignation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to update designation.";
      });
  },
});

export const { clearDesignations } = designationSlice.actions;
export default designationSlice.reducer;
