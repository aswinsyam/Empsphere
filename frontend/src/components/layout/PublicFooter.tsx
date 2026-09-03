/**
 * PublicFooter.
 *
 * Footer for the public website. Lists navigation, legal pages, and a
 * copyright line. Deliberately simple and dependency-free.
 */

import { Link } from "react-router-dom";
import { APP_NAME } from "@/utils/constants";

const PRODUCT_LINKS = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

const LEGAL_LINKS = [
  { to: "/terms", label: "Terms & Conditions" },
  { to: "/privacy", label: "Privacy Policy" },
  { to: "/cancellation-refund", label: "Cancellation & Refund Policy" },
];

export function PublicFooter() {
  const year = 2026;
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3 lg:px-8">
        <div>
          <Link to="/" className="flex items-center gap-2 text-slate-900">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
              E
            </span>
            <span className="text-base font-semibold tracking-tight">{APP_NAME}</span>
          </Link>
          <p className="mt-3 text-sm text-slate-600">
            An employee management platform that helps organizations manage
            people, attendance, leave, and internal services in one place.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-900">Product</h3>
          <ul className="mt-3 space-y-2">
            {PRODUCT_LINKS.map((link) => (
              <li key={link.to}>
                <Link
                  to={link.to}
                  className="text-sm text-slate-600 hover:text-slate-900"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-900">Legal</h3>
          <ul className="mt-3 space-y-2">
            {LEGAL_LINKS.map((link) => (
              <li key={link.to}>
                <Link
                  to={link.to}
                  className="text-sm text-slate-600 hover:text-slate-900"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-200">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-4 text-sm text-slate-500 sm:flex-row sm:px-6 lg:px-8">
          <p>© {year} {APP_NAME}. All rights reserved.</p>
          <p>Built for internal employee management.</p>
        </div>
      </div>
    </footer>
  );
}
