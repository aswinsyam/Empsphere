/**
 * useAuth hook.
 * Provides convenient access to the auth state and actions.
 */

import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/store";
import {
  clearAuth,
  fetchMe,
  googleLogin,
  login,
  login as loginAction,
  logoutUser,
  register,
} from "@/store/slices/authSlice";
import { LoginPayload, RegisterPayload } from "@/types/auth";
import { getDashboardRoute } from "@/utils/constants";

export function useAuth() {
  const dispatch = useDispatch<AppDispatch>();
  const { user, loading, initializing, error } = useSelector(
    (state: RootState) => state.auth
  );

  const isAuthenticated = Boolean(user);
  const dashboardRoute = getDashboardRoute(user?.role);

  const handleLogin = useCallback(
    (payload: LoginPayload) => dispatch(loginAction(payload)),
    [dispatch]
  );

  const handleRegister = useCallback(
    (payload: RegisterPayload) => dispatch(register(payload)),
    [dispatch]
  );

  const handleFetchMe = useCallback(() => dispatch(fetchMe()), [dispatch]);

  const handleLogout = useCallback(() => dispatch(logoutUser()), [dispatch]);

  const handleClearAuth = useCallback(() => dispatch(clearAuth()), [dispatch]);

  const handleGoogleLogin = useCallback(
    (idToken: string) => dispatch(googleLogin(idToken)),
    [dispatch]
  );

  return {
    user,
    isAuthenticated,
    initializing,
    loading,
    error,
    dashboardRoute,
    login: handleLogin,
    register: handleRegister,
    fetchMe: handleFetchMe,
    logout: handleLogout,
    clearAuth: handleClearAuth,
    googleLogin: handleGoogleLogin,
  };
}

// Re-export login for potential direct imports.
export { login };
