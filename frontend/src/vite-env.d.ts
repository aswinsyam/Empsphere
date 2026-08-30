/**
 * Vite type augmentation.
 *
 * Declares the shape of `import.meta.env` so TypeScript recognizes
 * the custom environment variables used by the frontend.
 * Corresponds to variables defined in `.env` / `.env.local`.
 */

/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_APP_URL?: string;
  readonly VITE_GOOGLE_CLIENT_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
