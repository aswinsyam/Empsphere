/**
 * AppBootstrap.
 *
 * Session-restoration component mounted at the application root.
 * On mount it checks for a stored access token and dispatches `fetchMe`
 * to validate the session. It also listens for `auth:expired` events
 * (dispatched by the axios interceptor) to clear auth state and redirect
 * to login when refresh tokens are exhausted.
 */

import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { AppDispatch } from "@/store";
import {
  clearAuth,
  fetchMe,
  setInitialized,
} from "@/store/slices/authSlice";
import { AUTH_EXPIRED_EVENT } from "@/config/axios";
import { TokenUtil } from "@/utils/token";
import { ROUTES } from "@/utils/constants";

export function AppBootstrap() {
  /**
   * Restores the session on app load by checking for a stored access
   * token and dispatching `fetchMe`. Also listens for `auth:expired`
   * events (dispatched by the axios interceptor) to clear auth state
   * and redirect to login when refresh tokens are exhausted.
   */
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  useEffect(() => {
    // Restore the session on load.
    const token = TokenUtil.getAccessToken();

    if (token) {
      dispatch(fetchMe());
    } else {
      dispatch(setInitialized());
    }
  }, [dispatch]);

  // Listen for the auth-expired event (refresh token no longer usable).
  useEffect(() => {
    const onAuthExpired = () => {
      TokenUtil.clear();
      dispatch(clearAuth());
      navigate(ROUTES.LOGIN, { replace: true });
    };

    window.addEventListener(AUTH_EXPIRED_EVENT, onAuthExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, onAuthExpired);
  }, [dispatch, navigate]);

  return null;
}
