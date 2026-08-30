/**
 * Attendance slice.
 * Manages attendance state with Redux Toolkit.
 */

import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { attendanceService } from "@/services/attendance.service";
import { AttendanceListResponse, AttendanceRecord, AttendanceSummary } from "@/types/attendance";

interface AttendanceState {
  records: AttendanceRecord[];
  summary: AttendanceSummary | null;
  loading: boolean;
  error: string | null;
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}

const initialState: AttendanceState = {
  records: [],
  summary: null,
  loading: false,
  error: null,
  page: 1,
  page_size: 10,
  total_records: 0,
  total_pages: 0,
};

export const fetchAttendance = createAsyncThunk<
  AttendanceListResponse,
  { employee_id?: string; start_date?: string; end_date?: string; status?: string; page?: number; page_size?: number }
>("attendance/fetchAll", async (params) => {
  const res = await attendanceService.list(params);
  return res;
});

export const markAttendance = createAsyncThunk<
  { attendance_id: string },
  {
    employee_id?: string;
    date: string;
    status?: string;
    check_in?: string;
    check_out?: string;
    remarks?: string;
  }
>("attendance/mark", async (payload) => {
  return attendanceService.mark(payload);
});

export const updateAttendance = createAsyncThunk<
  AttendanceRecord,
  { id: string; status?: string; check_in?: string; check_out?: string; remarks?: string }
>("attendance/update", async ({ id, ...payload }) => {
  return attendanceService.update(id, payload);
});

export const fetchAttendanceSummary = createAsyncThunk<
  AttendanceSummary,
  { employee_id: string; start_date?: string; end_date?: string }
>("attendance/fetchSummary", async (params) => {
  return attendanceService.summary(params.employee_id, params.start_date, params.end_date);
});

export const checkIn = createAsyncThunk<AttendanceRecord, void>(
  "attendance/checkIn",
  async () => {
    return attendanceService.checkIn();
  }
);

export const checkOut = createAsyncThunk<AttendanceRecord, void>(
  "attendance/checkOut",
  async () => {
    return attendanceService.checkOut();
  }
);

const attendanceSlice = createSlice({
  name: "attendance",
  initialState,
  reducers: {
    clearAttendance(state) {
      state.records = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAttendance.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchAttendance.fulfilled,
        (state, action: PayloadAction<AttendanceListResponse>) => {
          state.loading = false;
          state.records = action.payload.attendance;
          state.total_records = action.payload.total_records;
          state.total_pages = action.payload.total_pages;
          state.page = action.payload.page;
          state.page_size = action.payload.page_size;
        }
      )
      .addCase(fetchAttendance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load attendance.";
      })
      .addCase(markAttendance.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(markAttendance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to mark attendance.";
      })
      .addCase(updateAttendance.fulfilled, (state, action: PayloadAction<AttendanceRecord>) => {
        state.loading = false;
        const idx = state.records.findIndex((r) => r.attendance_id === action.payload.attendance_id);
        if (idx >= 0) {
          state.records[idx] = action.payload;
        }
      })
      .addCase(updateAttendance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to update attendance.";
      })
      .addCase(fetchAttendanceSummary.fulfilled, (state, action: PayloadAction<AttendanceSummary>) => {
        state.summary = action.payload;
      })
      .addCase(fetchAttendanceSummary.rejected, (state, action) => {
        state.error = action.error.message || "Failed to load attendance summary.";
      })
      .addCase(checkIn.fulfilled, (state, action: PayloadAction<AttendanceRecord>) => {
        state.loading = false;
        const idx = state.records.findIndex((r) => r.attendance_id === action.payload.attendance_id);
        if (idx >= 0) {
          state.records[idx] = action.payload;
        } else {
          state.records.unshift(action.payload);
        }
      })
      .addCase(checkIn.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to check in.";
      })
      .addCase(checkOut.fulfilled, (state, action: PayloadAction<AttendanceRecord>) => {
        state.loading = false;
        const idx = state.records.findIndex((r) => r.attendance_id === action.payload.attendance_id);
        if (idx >= 0) {
          state.records[idx] = action.payload;
        } else {
          state.records.unshift(action.payload);
        }
      })
      .addCase(checkOut.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to check out.";
      });
  },
});

export const { clearAttendance } = attendanceSlice.actions;
export default attendanceSlice.reducer;
