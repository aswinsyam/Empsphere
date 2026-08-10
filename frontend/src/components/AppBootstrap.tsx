/**
 * AppBootstrap.
 * Restores the authenticated session on app load by validating the
 * stored access token and fetching the current user profile.
 *
 * It also listens for the `auth:expired` event dispatched by the axios
 * interceptor when the refresh token can no longer restore auth, so the
 * app can clear auth state and redirect to login.
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
