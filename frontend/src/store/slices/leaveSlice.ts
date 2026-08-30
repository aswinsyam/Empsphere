/**
 * Leave slice.
 * Manages leave state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { leaveService } from "@/services/leave.service";
import { LeaveRecord } from "@/types/leave";

interface LeaveState {
  leaves: LeaveRecord[];
  total_records: number;
  total_pages: number;
  page: number;
  page_size: number;
  loading: boolean;
  error: string | null;
}

const initialState: LeaveState = {
  leaves: [],
  total_records: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
  loading: false,
  error: null,
};

export const fetchLeaves = createAsyncThunk<
  { leaves: LeaveRecord[]; total_records: number; total_pages: number; page: number; page_size: number },
  { employee_id?: string; status?: string; page?: number; page_size?: number }
>("leave/fetchAll", async (params) => {
  const res = await leaveService.list(params);
  return {
    leaves: res.leaves,
    total_records: res.total_records,
    total_pages: res.total_pages,
    page: res.page,
    page_size: res.page_size,
  };
});

export const applyLeave = createAsyncThunk<
  { leave_id: string },
  { employee_id: string; start_date: string; end_date: string; leave_type?: string; reason?: string }
>("leave/apply", async (payload) => {
  return leaveService.apply(payload);
});

export const updateLeaveStatus = createAsyncThunk<
  LeaveRecord,
  { id: string; status: "APPROVED" | "REJECTED" }
>("leave/updateStatus", async ({ id, status }) => {
  return leaveService.updateStatus(id, status);
});

const leaveSlice = createSlice({
  name: "leave",
  initialState,
  reducers: {
    clearLeaves(state) {
      state.leaves = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchLeaves.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchLeaves.fulfilled,
        (state, action: PayloadAction<{ leaves: LeaveRecord[]; total_records: number; total_pages: number; page: number; page_size: number }>) => {
          state.loading = false;
          state.leaves = action.payload.leaves;
          state.total_records = action.payload.total_records;
          state.total_pages = action.payload.total_pages;
          state.page = action.payload.page;
          state.page_size = action.payload.page_size;
        }
      )
      .addCase(fetchLeaves.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load leaves.";
      })
      .addCase(applyLeave.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(applyLeave.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to apply leave.";
      })
      .addCase(updateLeaveStatus.fulfilled, (state, action: PayloadAction<LeaveRecord>) => {
        state.loading = false;
        const idx = state.leaves.findIndex((l) => l.leave_id === action.payload.leave_id);
        if (idx >= 0) {
          state.leaves[idx] = action.payload;
        }
      })
      .addCase(updateLeaveStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to update leave status.";
      });
  },
});

export const { clearLeaves } = leaveSlice.actions;
export default leaveSlice.reducer;
