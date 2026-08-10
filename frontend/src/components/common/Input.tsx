/**
 * Input.
 * Reusable labeled input field.
 */

import { InputHTMLAttributes, ReactNode } from "react";
import { cn } from "@/utils/helpers";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: ReactNode;
}

export function Input({ label, error, hint, className, id, ...props }: InputProps) {
  const inputId = id || props.name;

  return (
    <div className="w-full">
      {label ? (
        <label htmlFor={inputId} className="label">
          {label}
        </label>
      ) : null}
      <input
        id={inputId}
        className={cn("input", error ? "border-red-500 focus:border-red-500 focus:ring-red-500" : "", className)}
        {...props}
      />
      {error ? <p className="mt-1 text-sm text-red-600">{error}</p> : null}
      {!error && hint ? <div className="mt-1 text-sm text-slate-500">{hint}</div> : null}
    </div>
  );
}
