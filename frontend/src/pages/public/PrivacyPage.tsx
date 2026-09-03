/**
 * Privacy Policy page.
 *
 * Public, no-auth. Describes how EmpSphere handles the limited categories
 * of data the platform actually collects: account, employee, authentication,
 * and payment-related data routed through Razorpay. No unverified
 * compliance certifications are claimed.
 */

import { Link } from "react-router-dom";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME } from "@/utils/constants";

const SECTIONS: { id: string; title: string; body: string[] }[] = [
  {
    id: "information-we-collect",
    title: "1. Information We Collect",
    body: [
      `${APP_NAME} collects only the information needed to operate its core features: account information, employee records, authentication events, audit logs, and payment records for office amenities.`,
    ],
  },
  {
    id: "account-information",
    title: "2. Account Information",
    body: [
      "When an account is created, we collect basic information such as your name, email, and (depending on your organization) an employee code.",
      "If you sign in with Google, we receive the basic profile information that Google makes available to the application.",
    ],
  },
  {
    id: "employee-information",
    title: "3. Employee Information",
    body: [
      "Once onboarded, additional employee information may be added by an administrator, such as department, designation, contact details, and profile image.",
      "This information is used to power features such as attendance tracking, leave workflows, and reporting.",
    ],
  },
  {
    id: "authentication-information",
    title: "4. Authentication Information",
    body: [
      `${APP_NAME} uses JSON Web Tokens (JWT) for session management and records login and password-reset events for security and audit purposes.`,
      "Passwords are stored as secure hashes and are never stored or transmitted in plain text.",
    ],
  },
  {
    id: "payment-information",
    title: "5. Payment Information",
    body: [
      "When you initiate a payment for an office amenity, the platform records the payment reference returned by the payment provider, the status, and the amount.",
      "Sensitive payment credentials (such as full card numbers, CVV, or online-banking passwords) are not stored by EmpSphere. They are handled directly by the payment provider in line with their security standards.",
    ],
  },
  {
    id: "how-information-is-used",
    title: "6. How Information Is Used",
    body: [
      "We use the information we collect to operate and improve the platform's features, to authenticate users, to process payments, to generate reports requested by administrators, and to maintain an audit trail of significant actions.",
      "We do not sell your personal information to third parties.",
    ],
  },
  {
    id: "data-storage",
    title: "7. Data Storage",
    body: [
      "Business data is stored in a MongoDB database operated by your organization. Authentication-related data is stored in the database used by the Django backend.",
      "Profile images, if uploaded, are stored within the backend's storage layer.",
    ],
  },
  {
    id: "payment-processing",
    title: "8. Payment Processing",
    body: [
      "All payments for office amenities are processed by Razorpay. Razorpay acts as an independent data controller for the payment data it processes. We recommend that you also review Razorpay's privacy policy for details on how they handle your payment data.",
    ],
  },
  {
    id: "third-party-services",
    title: "9. Third-Party Services",
    body: [
      `${APP_NAME} relies on a small set of third-party services to operate, including Razorpay for payments and Google for sign-in. These services may receive limited information required to perform their function (for example, your email when you sign in with Google).`,
    ],
  },
  {
    id: "data-security",
    title: "10. Data Security",
    body: [
      "We use industry-standard technical and organizational measures to protect data, including hashed passwords, signed authentication tokens, signed payment webhooks, and role-based access controls.",
      "No system is perfectly secure; if you become aware of a security issue, please contact your organization's administrator.",
    ],
  },
  {
    id: "data-retention",
    title: "11. Data Retention",
    body: [
      "We retain employee records, attendance, leave, and payment records for as long as your organization keeps the corresponding data in the platform, in line with your organization's internal retention policy.",
      "Audit logs are retained for a rolling 30-day window by default.",
    ],
  },
  {
    id: "user-rights",
    title: "12. User Rights",
    body: [
      "You can review and update much of your own information from the Profile page in the platform.",
      "For requests to correct or delete data that you cannot change yourself, please contact your organization's administrator.",
    ],
  },
  {
    id: "policy-changes",
    title: "13. Policy Changes",
    body: [
      "This Privacy Policy may be updated from time to time. The latest version will always be available on this page along with the effective date.",
    ],
  },
  {
    id: "contact",
    title: "14. Contact",
    body: [
      "For privacy-related questions, please use the information on the Contact page to reach the appropriate team.",
    ],
  },
];

export function PrivacyPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Privacy Policy`}
        description={`How ${APP_NAME} collects, uses, and protects your information.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            Privacy Policy
          </h1>
          <p className="mt-3 text-sm text-slate-500">
            Effective date: 1 January 2026
          </p>
          <p className="mt-4 text-base text-slate-600">
            This Privacy Policy explains how {APP_NAME} handles the information
            it collects when you use the platform.
          </p>
        </div>
      </section>

      <section className="bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="space-y-8">
            {SECTIONS.map((section) => (
              <article
                key={section.id}
                id={section.id}
                className="rounded-xl border border-slate-200 bg-white p-6 shadow-card"
              >
                <h2 className="text-lg font-semibold text-slate-900">
                  {section.title}
                </h2>
                <div className="mt-3 space-y-2 text-sm text-slate-600">
                  {section.body.map((p, idx) => (
                    <p key={idx}>{p}</p>
                  ))}
                </div>
              </article>
            ))}

            <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-card">
              For information about how we handle payments, please also see our{" "}
              <Link
                to="/cancellation-refund"
                className="text-brand-700 hover:text-brand-800"
              >
                Cancellation & Refund Policy
              </Link>
              .
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
