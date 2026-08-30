/**
 * Configured Axios instance.
 * - Base URL from env.
 * - Attaches the access token to every request except public endpoints.
 * - Attempts token refresh on 401 once before retrying.
 * - Stores both new tokens when the backend rotates the refresh token.
 * - Clears auth and notifies the app when refresh fails.
 */

import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";
import { ENV } from "./env";
import { TokenUtil } from "@/utils/token";

/** Extend axios config to optionally skip the auth interceptor. */
declare module "axios" {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

/** Public auth endpoints that do not require an access token. */
const PUBLIC_AUTH_ENDPOINTS = [
  "/auth/login/",
  "/auth/register/",
  "/auth/logout/",
  "/auth/refresh-token/",
  "/auth/verify-email/",
  "/auth/google-login/",
  "/auth/send-otp/",
  "/auth/verify-otp/",
  "/auth/set-password/",
];

function isPublicEndpoint(url: string | undefined): boolean {
  if (!url) return false;
  return PUBLIC_AUTH_ENDPOINTS.some((endpoint) => url.includes(endpoint));
}

/** Custom event fired when the refresh token can no longer restore auth. */
export const AUTH_EXPIRED_EVENT = "auth:expired";

/** Dispatch a custom event so the app can clear auth and redirect to login. */
function dispatchAuthExpired() {
  window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
}

export const api: AxiosInstance = axios.create({
  baseURL: ENV.API_BASE_URL,
});

// Attach access token to every request except public endpoints.
api.interceptors.request.use((config) => {
  if (!isPublicEndpoint(config.url)) {
    const token = TokenUtil.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// On 401, try to refresh the token and retry once.
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isPublicEndpoint(original.url)
    ) {
      original._retry = true;
      const refreshToken = TokenUtil.getRefreshToken();
      if (refreshToken) {
        try {
          const result = await axios.post<{ access_token: string; refresh_token: string }>(
            `${ENV.API_BASE_URL}/auth/refresh-token/`,
            { refresh_token: refreshToken }
          );
          const newAccessToken = result.data.access_token;
          const newRefreshToken = result.data.refresh_token;
          TokenUtil.setTokens(newAccessToken, newRefreshToken);
          original.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(original);
        } catch {
          TokenUtil.clear();
          dispatchAuthExpired();
        }
      }
    }
    return Promise.reject(error);
  }
);
