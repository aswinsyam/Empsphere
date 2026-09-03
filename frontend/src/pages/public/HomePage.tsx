/**
 * Public Home page.
 *
 * Landing page for the EmpSphere public website. No authentication is
 * required. Content reflects the actual platform features (employee,
 * attendance, leave, departments/designations, reports, payments,
 * authentication). External links to Razorpay and registration go to the
 * existing internal routes.
 */

import { Link } from "react-router-dom";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME, ROUTES } from "@/utils/constants";

interface Feature {
  title: string;
  description: string;
  icon: string;
}

const FEATURES: Feature[] = [
  {
    title: "Employee Management",
    description:
      "Maintain a single source of truth for employee records, profiles, and access roles.",
    icon: "M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4",
  },
  {
    title: "Attendance",
    description:
      "Track daily check-in and check-out with a clean attendance view for employees and managers.",
    icon: "M8 7V3m8 4V3M3 11h18M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  {
    title: "Leave Management",
    description:
      "Apply for leave and approve or reject requests from a dedicated workflow with a full audit trail.",
    icon: "M9 12h6m-6 4h6M5 7h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z",
  },
  {
    title: "Departments & Designations",
    description:
      "Organize employees under departments and roles so reporting, filters, and permissions stay consistent.",
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16M9 7h1m-1 4h1m4-4h1m-1 4h1",
  },
  {
    title: "Reports & Statistics",
    description:
      "Get an at-a-glance view of attendance, leave, and activity with built-in reports for managers.",
    icon: "M9 17v-6m4 6V7m4 10v-3M3 21h18",
  },
  {
    title: "Office Amenities & Payments",
    description:
      "Pay for office amenities such as ID cards, kits, and event fees through Razorpay with verification on the server.",
    icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3 7.5h18M5.25 6v12",
  },
  {
    title: "Secure Authentication",
    description:
      "JWT-based authentication, Google sign-in, password reset, and OTP verification are all available out of the box.",
    icon: "M16 11V7a4 4 0 10-8 0v4M5 11h14v10H5z",
  },
  {
    title: "Activity Logs",
    description:
      "Every important action is recorded so administrators can review who did what and when.",
    icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
  },
];

export function HomePage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Employee Management Platform`}
        description="EmpSphere is an employee management platform that brings employees, attendance, leave, and office services into one place."
      />

      {/* Hero */}
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8 lg:py-24">
          <div className="grid items-center gap-10 md:grid-cols-2">
            <div>
              <span className="inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                Employee Management Platform
              </span>
              <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
                Manage your team in one place with {APP_NAME}.
              </h1>
              <p className="mt-4 text-base text-slate-600 sm:text-lg">
                {APP_NAME} is an employee management platform designed to help
                organizations manage employees, attendance, leave management,
                and company-related services from a single dashboard.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to={ROUTES.LOGIN} className="btn-primary">
                  Get Started
                </Link>
                <Link to={ROUTES.REGISTER} className="btn-ghost">
                  Create an account
                </Link>
              </div>
              <p className="mt-4 text-xs text-slate-500">
                Payments for office amenities are processed through Razorpay.
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 shadow-card">
              <div className="grid grid-cols-2 gap-4">
                {FEATURES.slice(0, 4).map((feature) => (
                  <div
                    key={feature.title}
                    className="rounded-xl border border-slate-200 bg-white p-4"
                  >
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-5 w-5"
                        aria-hidden="true"
                      >
                        <path d={feature.icon} />
                      </svg>
                    </div>
                    <h3 className="mt-3 text-sm font-semibold text-slate-900">
                      {feature.title}
                    </h3>
                    <p className="mt-1 text-xs text-slate-600">
                      {feature.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-2xl font-semibold text-slate-900 sm:text-3xl">
              Everything you need to run people operations
            </h2>
            <p className="mt-3 text-sm text-slate-600 sm:text-base">
              {APP_NAME} is built around the workflows that small and mid-size
              teams actually use every day.
            </p>
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-card"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-5 w-5"
                    aria-hidden="true"
                  >
                    <path d={feature.icon} />
                  </svg>
                </div>
                <h3 className="mt-4 text-sm font-semibold text-slate-900">
                  {feature.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About */}
      <section className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid items-start gap-10 md:grid-cols-2">
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 sm:text-3xl">
                About {APP_NAME}
              </h2>
              <p className="mt-4 text-sm text-slate-600 sm:text-base">
                {APP_NAME} brings together the everyday operations that
                organizations need to run a healthy team: employee records,
                attendance, leave, departments and designations, activity
                auditing, and payments for office amenities.
              </p>
              <p className="mt-3 text-sm text-slate-600 sm:text-base">
                It is designed for organizations that want a single, reliable
                system of record for their people operations without juggling
                multiple disconnected tools.
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <h3 className="text-base font-semibold text-slate-900">
                Intended users
              </h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>• Super Admins and Admins managing the platform</li>
                <li>• HR Managers handling people operations</li>
                <li>• Employees using self-service features</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-card sm:flex-row sm:text-left">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">
                Have a question?
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                Reach out through our contact page and we will route your
                enquiry to the right team.
              </p>
            </div>
            <Link to="/contact" className="btn-primary">
              Contact us
            </Link>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
