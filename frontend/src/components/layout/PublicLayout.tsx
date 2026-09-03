/**
 * PublicLayout.
 *
 * Shared shell for the public-facing marketing/legal pages (Home, About,
 * Contact, Terms, Privacy, Cancellation & Refund). It renders a public
 * header, the routed page content, and a public footer. It deliberately
 * does NOT use the authenticated `DashboardLayout` (no sidebar, no
 * ProtectedRoute, no auth checks).
 */

import { ReactNode } from "react";
import { PublicHeader } from "./PublicHeader";
import { PublicFooter } from "./PublicFooter";

interface PublicLayoutProps {
  children: ReactNode;
}

export function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <PublicHeader />
      <main className="flex-1">{children}</main>
      <PublicFooter />
    </div>
  );
}
