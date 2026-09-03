/**
 * AuthPageShell.
 *
 * Shared layout wrapper for all public authentication pages. Provides
 * consistent branding, centered card layout, and responsive padding so
 * that individual auth pages only need to supply their form content.
 */

interface AuthPageShellProps {
  /** Page title shown in the heading. */
  title: string;
  /** Optional subtitle shown below the title. */
  subtitle?: string;
  /** Form or content rendered inside the branded card. */
  children: React.ReactNode;
}

export function AuthPageShell({ title, subtitle, children }: AuthPageShellProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-brand-600">{title}</h1>
          {subtitle && (
            <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
          )}
        </div>

        <div className="card p-6">{children}</div>
      </div>
    </div>
  );
}
