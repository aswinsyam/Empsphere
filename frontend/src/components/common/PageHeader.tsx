/**
 * PageHeader.
 *
 * Consistent page title block with optional subtitle and action buttons
 * (e.g. "Create" or "Save"). Used at the top of protected pages to
 * provide context and quick access to primary actions.
 */

import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  /**
   * Consistent page header with title, optional subtitle, and an optional
   * action slot (e.g. a "Create" button). Used at the top of protected
   * pages to provide context and primary actions.
   */
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  );
}
