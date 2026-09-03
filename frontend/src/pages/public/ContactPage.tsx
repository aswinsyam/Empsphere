/**
 * Contact page.
 *
 * Public, no-auth. Because no verified business contact details exist in
 * the project, the page intentionally avoids inventing a phone, address,
 * or email. It points users to the organization's administrator and
 * lists the existing in-app contact surface (login-required support
 * flows).
 */

import { Link } from "react-router-dom";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME, ROUTES } from "@/utils/constants";

export function ContactPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Contact`}
        description={`How to get in touch with the ${APP_NAME} team.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            Contact us
          </h1>
          <p className="mt-4 text-base text-slate-600">
            We want to make it easy to reach us for support, account questions,
            or general enquiries about {APP_NAME}.
          </p>
        </div>
      </section>

      <section className="bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                General enquiries
              </h2>
              <p className="mt-3 text-sm text-slate-600">
                For support or general enquiries, please contact the
                {" "}{APP_NAME} administration team through the contact
                information provided by your organization.
              </p>
              <p className="mt-3 text-sm text-slate-600">
                If you already have an account, you can change your password,
                update your profile, and reach support through the in-app
                account menu.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">
                Existing users
              </h2>
              <p className="mt-3 text-sm text-slate-600">
                If you are an existing user of {APP_NAME}, please sign in to
                access your profile, password reset, and activity history.
              </p>
              <div className="mt-4 flex flex-wrap gap-3">
                <Link to={ROUTES.LOGIN} className="btn-primary">
                  Go to login
                </Link>
                <Link to={ROUTES.FORGOT_PASSWORD} className="btn-ghost">
                  Forgot password
                </Link>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-card md:col-span-2">
              <h2 className="text-lg font-semibold text-slate-900">
                Payment-related enquiries
              </h2>
              <p className="mt-3 text-sm text-slate-600">
                For questions about a specific payment, please refer to our
                {" "}<Link to="/cancellation-refund" className="text-brand-700 hover:text-brand-800">Cancellation & Refund Policy</Link>
                {" "}and reach out to your organization&apos;s administrator
                with the payment reference shown in your payment history.
              </p>
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
