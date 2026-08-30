/**
 * Redux store configuration.
 *
 * Registers the top-level slices (`auth`, `department`) and appends
 * `authMiddleware` to the default middleware chain. This store is
 * provided to the React component tree via `Provider` in `App.tsx`.
 */

import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import departmentReducer from "./slices/departmentSlice";
import designationReducer from "./slices/designationSlice";
import employeeReducer from "./slices/employeeSlice";
import attendanceReducer from "./slices/attendanceSlice";
import leaveReducer from "./slices/leaveSlice";
import paymentReducer from "./slices/paymentSlice";
import { authMiddleware } from "./middleware/authMiddleware";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    department: departmentReducer,
    designation: designationReducer,
    employee: employeeReducer,
    attendance: attendanceReducer,
    leave: leaveReducer,
    payment: paymentReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(authMiddleware),
});

// Infer the `RootState` and `AppDispatch` types from the store.
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
