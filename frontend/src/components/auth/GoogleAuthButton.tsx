/**
 * GoogleAuthButton.
 *
 * Renders the Google "Continue with Google" button using Google Identity
 * Services (GIS). Loads the GIS script implicitly and passes the
 * resulting ID token to the `onCredential` callback. Gracefully handles
 * missing client ID or failed script load with an error message.
 *
 * @param onCredential - Called with the Google ID token on successful sign-in.
 */

import { useEffect, useRef, useState } from "react";
import { ENV } from "@/config/env";

/** Google Identity Services account ID API surface. */
interface GoogleAccountsId {
  initialize: (config: {
    client_id: string;
    callback: (response: { credential: string }) => void;
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options?: Record<string, unknown>
  ) => void;
}

/** Minimal shape of the global `google` object injected by the GSI script. */
interface GoogleGlobal {
  accounts?: { id?: GoogleAccountsId };
}

/** Shape of `window` augmented with the GSI `google` global. */
interface WindowWithGoogle extends Window {
  google?: GoogleGlobal;
}

interface GoogleAuthButtonProps {
  /** Called with the Google ID token once the user authenticates. */
  onCredential: (credential: string) => void;
}

let googleInitialized = false;
let globalCallback: ((credential: string) => void) | null = null;

export function GoogleAuthButton({ onCredential }: GoogleAuthButtonProps) {
  /**
   * Renders the Google "Continue with Google" button using Google
   * Identity Services (GIS). Passes the resulting ID token to the
   * `onCredential` callback. Handles missing client ID and script load
   * failures gracefully.
   */
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const clientId = ENV.GOOGLE_CLIENT_ID;

    if (!clientId) {
      setError(
        "Google login is not configured. Set VITE_GOOGLE_CLIENT_ID in frontend/.env and GOOGLE_CLIENT_ID in backend/.env."
      );
      return;
    }

    const google = (window as unknown as WindowWithGoogle).google;
    const id = google?.accounts?.id;

    if (!id) {
      setError(
        "Google Identity Services failed to load. Check your internet connection and try again."
      );
      return;
    }

    globalCallback = (credential: string) => onCredential(credential);

    if (!googleInitialized) {
      id.initialize({
        client_id: clientId,
        callback: (response) => {
          if (globalCallback) {
            globalCallback(response.credential);
          }
        },
      });
      googleInitialized = true;
    }

    if (containerRef.current) {
      id.renderButton(containerRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        text: "continue_with",
      });
    }
  }, [onCredential]);

  if (error) {
    return (
      <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-700">
        {error}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex justify-center"
      aria-label="Continue with Google"
    />
  );
}
