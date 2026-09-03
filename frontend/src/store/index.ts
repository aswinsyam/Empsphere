/**
 * Redux store configuration.
 *
 * Only the auth slice is kept globally — all other state is managed
 * with local component state via services directly.
 */

import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
