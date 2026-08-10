/**
 * Token storage helpers.
 * Stores the access and refresh tokens in localStorage.
 */

const ACCESS_TOKEN_KEY = "emp_access_token";
const REFRESH_TOKEN_KEY = "emp_refresh_token";

export const TokenUtil = {
  /** Get the access token. */
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /** Get the refresh token. */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  /** Save both tokens. */
  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  /** Set just the access token (after refresh). */
  setAccessToken(accessToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  },

  /** Remove all tokens (logout). */
  clear(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};
