/**
 * Terms & Conditions page.
 *
 * Public, no-auth. Written for an internal employee management platform
 * (EmpSphere). Avoids unverifiable legal-entity claims; names Razorpay as
 * the payment processor.
 */

import { Link } from "react-router-dom";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME } from "@/utils/constants";

const SECTIONS: { id: string; title: string; body: string[] }[] = [
  {
    id: "introduction",
    title: "1. Introduction",
    body: [
      `These Terms & Conditions govern your use of ${APP_NAME}, a web-based employee management platform. By accessing or using ${APP_NAME}, you agree to be bound by these Terms.`,
      `${APP_NAME} is provided to authorized users of organizations that have chosen to operate the platform. Use of the platform is subject to your organization's internal policies in addition to these Terms.`,
    ],
  },
  {
    id: "use-of-the-platform",
    title: "2. Use of the Platform",
    body: [
      `${APP_NAME} is intended for managing employee records, attendance, leave, departments, designations, reports, and approved office services such as amenity payments.`,
      "You agree to use the platform only for purposes that are lawful and consistent with your role inside the operating organization.",
      "You must not attempt to access data, accounts, or areas of the platform that you are not authorized to use.",
    ],
  },
  {
    id: "user-accounts",
    title: "3. User Accounts",
    body: [
      "You are responsible for keeping your account credentials (such as your email and password) confidential.",
      "You agree to notify your organization's administrator immediately if you believe your account has been compromised.",
      `${APP_NAME} may suspend or terminate accounts that violate these Terms or that are no longer associated with an active member of the operating organization.`,
    ],
  },
  {
    id: "employee-information",
    title: "4. Employee Information",
    body: [
      "Employee data (such as name, contact details, department, designation, attendance, leave history, and activity logs) is stored and processed to operate the platform's core features.",
      "Access to this data is restricted based on your role (for example, Super Admin, Admin, HR Manager, or Employee).",
      "You are responsible for ensuring that any personal information you provide through the platform is accurate and kept up to date.",
    ],
  },
  {
    id: "payments-and-services",
    title: "5. Payments and Services",
    body: [
      `${APP_NAME} supports payments for office amenities defined by your organization (for example, ID cards, training material, event registrations, or equipment service).`,
      "The amount charged for any amenity is determined by your organization's administrator and is shown to you before you confirm the payment.",
      "All payments are processed by the payment provider described in Section 6.",
    ],
  },
  {
    id: "payment-processing",
    title: "6. Payment Processing",
    body: [
      "Payments made through the platform are processed by Razorpay, a third-party payment service provider.",
      `${APP_NAME} does not store your full card or banking details. Sensitive payment credentials are handled directly by the payment provider in line with their security standards.`,
      "By initiating a payment, you agree to Razorpay's applicable terms and policies in addition to these Terms.",
    ],
  },
  {
    id: "refunds-and-cancellations",
    title: "7. Refunds and Cancellations",
    body: [
      "Cancellation and refund eligibility depends on the type of amenity or service and your organization's applicable policy.",
      "Please review the Cancellation & Refund Policy for details on how to request a cancellation or report a failed or duplicate payment.",
    ],
  },
  {
    id: "intellectual-property",
    title: "8. Intellectual Property",
    body: [
      `The ${APP_NAME} name, design, and code are the property of their respective owners.`,
      "You may not copy, redistribute, or resell any part of the platform without written permission.",
    ],
  },
  {
    id: "prohibited-activities",
    title: "9. Prohibited Activities",
    body: [
      "You must not attempt to interfere with the platform's security, perform unauthorized automated requests, or upload malicious content.",
      "You must not use the platform to harass, defame, or discriminate against other users.",
    ],
  },
  {
    id: "availability",
    title: "10. Availability of the Platform",
    body: [
      `${APP_NAME} aims to keep the platform available, but it does not guarantee uninterrupted access. Maintenance, updates, or events outside of our control may affect availability.`,
    ],
  },
  {
    id: "limitation-of-liability",
    title: "11. Limitation of Liability",
    body: [
      `${APP_NAME} is provided on an "as is" basis. To the maximum extent permitted by law, ${APP_NAME} and its operators are not liable for any indirect, incidental, or consequential damages arising from your use of the platform.`,
    ],
  },
  {
    id: "changes-to-terms",
    title: "12. Changes to Terms",
    body: [
      "These Terms may be updated from time to time. The latest version will always be available on this page along with the effective date.",
    ],
  },
  {
    id: "contact",
    title: "13. Contact",
    body: [
      "If you have questions about these Terms, please use the information on the Contact page to reach the appropriate team.",
    ],
  },
];

export function TermsPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Terms & Conditions`}
        description={`The terms and conditions that govern the use of ${APP_NAME}.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            Terms & Conditions
          </h1>
          <p className="mt-3 text-sm text-slate-500">
            Effective date: 1 January 2026
          </p>
          <p className="mt-4 text-base text-slate-600">
            Please read these Terms & Conditions carefully before using
            {" "}{APP_NAME}. By using the platform, you agree to these Terms.
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
              For information about how we handle personal data, please see our{" "}
              <Link to="/privacy" className="text-brand-700 hover:text-brand-800">
                Privacy Policy
              </Link>
              .
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
