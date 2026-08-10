/**
 * Environment configuration.
 * Centralizes all environment variables used by the frontend.
 */

const getEnv = (key: string, fallback = ""): string => {
  const value = (import.meta.env as Record<string, string | undefined>)[key];
  return value ?? fallback;
};

export const ENV = {
  /** Base URL of the backend API. */
  API_BASE_URL: getEnv("VITE_API_BASE_URL", "http://127.0.0.1:8000/api"),
  /** Frontend app URL (used for email links). */
  APP_URL: getEnv("VITE_APP_URL", "http://localhost:3000"),
  /** Google OAuth client id (optional). */
  GOOGLE_CLIENT_ID: getEnv("VITE_GOOGLE_CLIENT_ID"),
};
