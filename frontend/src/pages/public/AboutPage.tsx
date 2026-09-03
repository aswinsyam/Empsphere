/**
 * About page.
 *
 * Public, no-auth. Describes what EmpSphere is, the problem it solves,
 * the main functionality, intended users, and the general purpose of the
 * platform. Avoids unverifiable claims.
 */

import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME } from "@/utils/constants";

export function AboutPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | About`}
        description={`Learn about ${APP_NAME} — an employee management platform for organizations that want to centralize people operations.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            About {APP_NAME}
          </h1>
          <p className="mt-4 text-base text-slate-600">
            {APP_NAME} is a web-based employee management platform that helps
            organizations run their day-to-day people operations from a single
            place. It centralizes records, attendance, leave, departments and
            designations, reporting, and payment-based office services.
          </p>
        </div>
      </section>

      <section className="bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                The problem we solve
              </h2>
              <p className="mt-3 text-sm text-slate-600">
                Many small and mid-size organizations still rely on a mix of
                spreadsheets, email approvals, and chat tools to manage their
                team. {APP_NAME} replaces this with a structured workflow that
                keeps records consistent, auditable, and easy to retrieve.
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                What it does
              </h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>• Centralizes employee records and profiles</li>
                <li>• Tracks attendance with check-in / check-out</li>
                <li>• Manages leave applications and approvals</li>
                <li>• Organizes departments and designations</li>
                <li>• Generates reports for HR and management</li>
                <li>• Collects payments for office amenities via Razorpay</li>
              </ul>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                Intended users
              </h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>• <strong>Super Admin / Admin</strong> — platform owners</li>
                <li>• <strong>HR Manager</strong> — people operations</li>
                <li>• <strong>Employee</strong> — self-service</li>
              </ul>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                Platform purpose
              </h2>
              <p className="mt-3 text-sm text-slate-600">
                The platform is intended to be a single system of record for
                internal employee data and workflows. It is not a public job
                board or recruitment platform; access is restricted to users
                associated with the operating organization.
              </p>
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
