/**
 * Generic utility helpers.
 */

/** A single password requirement item for live validation UIs. */
export interface PasswordRequirement {
  label: string;
  met: boolean;
}

/**
 * Returns the four password-strength checks that mirror the backend's
 * `PASSWORD_REGEX` in ``backend/apps/common/core/regex.py``.
 *
 * The backend requires:
 *   1. 8+ characters
 *   2. at least one uppercase letter
 *   3. at least one lowercase letter
 *   4. at least one digit
 */
export function getPasswordRequirements(password: string): PasswordRequirement[] {
  return [
    { label: "At least 8 characters", met: password.length >= 8 },
    { label: "One uppercase letter", met: /[A-Z]/.test(password) },
    { label: "One lowercase letter", met: /[a-z]/.test(password) },
    { label: "One number", met: /\d/.test(password) },
  ];
}


/** Simple class-name joiner (like clsx). */
export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

/** Format an ISO date string into a readable date. */
export function formatDate(value?: string | null): string {
  if (!value) return "-";
  try {
    return new Date(value).toLocaleDateString();
  } catch {
    return "-";
  }
}

/** Format an ISO date string into readable date + time. */
export function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return "-";
  }
}

/**
 * Extract a human-friendly error message from an API error.
 *
 * The backend returns a standardized error envelope:
 *   { success: false, message: "...", errors: null }
 *
 * For DRF serializer validation errors, the message is generic
 * ("Request validation failed.") and the real detail lives inside
 * the `errors` object, e.g.:
 *   { "new_password": ["Password must be at least 8 characters..."] }
 *
 * This helper prefers the specific field error from `errors` when
 * available, then falls back to the top-level message, then to the
 * Axios error message.
 */
export function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object") {
    const err = error as {
      response?: { data?: { message?: string; errors?: unknown } };
      message?: string;
    };

    const data = err.response?.data;

    // 1. If `errors` is an object of field → [message] pairs, pull the
    //    first nested message (most specific / user-friendly).
    if (
      data?.errors &&
      typeof data.errors === "object" &&
      !Array.isArray(data.errors)
    ) {
      const errorsObj = data.errors as Record<string, unknown>;
      const firstField = Object.keys(errorsObj)[0];
      const firstValue = firstField ? errorsObj[firstField] : undefined;

      if (typeof firstValue === "string" && firstValue.trim()) {
        return firstValue;
      }
      if (
        Array.isArray(firstValue) &&
        firstValue.length > 0 &&
        typeof firstValue[0] === "string"
      ) {
        return firstValue[0];
      }
    }

    // 2. Fall back to the backend's standardized message field.
    if (data?.message) return data.message;

    // 3. Fall back to a direct message property (e.g. non-Axios errors).
    if (err.message) return err.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}
