/**
 * Cancellation & Refund Policy page.
 *
 * Public, no-auth. Written specifically to be helpful during Razorpay
 * merchant website verification. It explains how to cancel a payment,
 * how refunds are handled, what happens for failed or duplicate payments,
 * and how long refunds may take — without inventing a specific
 * turnaround time or unverifiable business contact details.
 */

import { Link } from "react-router-dom";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME, ROUTES } from "@/utils/constants";

export function CancellationRefundPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Cancellation & Refund Policy`}
        description={`How to request a cancellation, how refunds are processed, and what happens for failed or duplicate payments on ${APP_NAME}.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            Cancellation & Refund Policy
          </h1>
          <p className="mt-3 text-sm text-slate-500">
            Effective date: 1 January 2026
          </p>
          <p className="mt-4 text-base text-slate-600">
            This page explains how cancellations and refunds work for office
            amenity payments made through {APP_NAME}.
          </p>
        </div>
      </section>

      <section className="bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="space-y-8">
            <article id="scope" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Scope</h2>
              <p className="mt-3 text-sm text-slate-600">
                {APP_NAME} allows employees to pay for office amenities (such
                as ID cards, training material, company events, or equipment
                service) using the payment provider integrated into the
                platform. This policy explains how cancellation and refund
                requests are handled for those payments.
              </p>
            </article>

            <article id="cancellation" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Cancellation</h2>
              <p className="mt-3 text-sm text-slate-600">
                A payment that is still marked as <strong>PENDING</strong> in
                your payment history can be cancelled from the Payments page
                inside the platform. Once a payment has been completed (status
                <strong> PAID</strong>) it is no longer eligible for
                self-service cancellation and may need to be reviewed as a
                refund request instead.
              </p>
              <p className="mt-3 text-sm text-slate-600">
                If you cannot find the payment in your history, sign in and
                visit <Link to={ROUTES.PAYMENTS} className="text-brand-700 hover:text-brand-800">Payments</Link>{" "}
                or contact your organization&apos;s administrator.
              </p>
            </article>

            <article id="refunds" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Refunds</h2>
              <p className="mt-3 text-sm text-slate-600">
                Refund eligibility depends on the type of amenity or service
                and the policy of the operating organization. Some amenities
                (for example, a customized or dispatched item) may not be
                refundable once processed.
              </p>
              <p className="mt-3 text-sm text-slate-600">
                If you believe a completed payment should be reviewed for a
                refund, please contact your organization&apos;s administrator
                with the payment reference shown in your payment history. The
                administrator will review the request and, where appropriate,
                initiate a refund.
              </p>
            </article>

            <article id="failed-payments" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Failed payments</h2>
              <p className="mt-3 text-sm text-slate-600">
                If a payment fails at the payment provider (for example, due
                to insufficient funds, a declined card, or a network error),
                the payment record will reflect a <strong>FAILED</strong>{" "}
                status. No amount is captured for a failed payment, and you
                can safely try again from the Payments page.
              </p>
            </article>

            <article id="duplicate-payments" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Duplicate or incorrect payments</h2>
              <p className="mt-3 text-sm text-slate-600">
                If you believe a payment was charged twice, charged the wrong
                amount, or charged for the wrong amenity, please report it to
                your organization&apos;s administrator as soon as possible.
                Include the payment reference, the date, and a short
                description of the issue so the administrator can review and
                reconcile it.
              </p>
            </article>

            <article id="refund-processing" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Refund processing</h2>
              <p className="mt-3 text-sm text-slate-600">
                Approved refunds are processed through the same payment
                provider used for the original payment. The time it takes for
                a refund to appear in your account depends on your bank or
                card issuer and on the payment method used.
              </p>
              <p className="mt-3 text-sm text-slate-600">
                {APP_NAME} does not control the settlement timeline once a
                refund has been initiated at the payment provider, and we
                cannot guarantee a specific number of business days for the
                refund to reflect in your account.
              </p>
            </article>

            <article id="contact" className="rounded-xl border border-slate-200 bg-white p-6 shadow-card">
              <h2 className="text-lg font-semibold text-slate-900">Contact</h2>
              <p className="mt-3 text-sm text-slate-600">
                For any cancellation, refund, or payment-related enquiry,
                please reach out to your organization&apos;s administrator
                first. General information is also available on the{" "}
                <Link to="/contact" className="text-brand-700 hover:text-brand-800">Contact</Link>{" "}
                page.
              </p>
            </article>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
