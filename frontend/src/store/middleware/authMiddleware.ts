/**
 * Auth middleware.
 * Listens for auth-related actions and keeps the store in sync.
 */

import { Middleware, isAnyOf } from "@reduxjs/toolkit";
import { TokenUtil } from "@/utils/token";
import { login, logoutUser } from "@/store/slices/authSlice";

/**
 * Persists/clears tokens and could dispatch additional side effects
 * when auth state changes.
 */
export const authMiddleware: Middleware =
  () => (next) => (action) => {
    if (isAnyOf(login.fulfilled)(action)) {
      // Tokens are already stored in the login thunk.
    }

if (isAnyOf(logoutUser.fulfilled)(action)) {
      TokenUtil.clear();
    }

    return next(action);
  };
