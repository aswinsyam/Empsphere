/**
 * Shipping Policy page.
 *
 * Public, no-auth. Required for Razorpay website verification. Explains that
 * EmpSphere is a digital employee-management platform and does not ship
 * physical products — all services and features are delivered electronically.
 * Avoids inventing a company address, phone number, email, registration
 * details, or legal claims.
 */

import { PublicLayout } from "@/components/layout/PublicLayout";
import { PageMeta } from "@/components/common/PageMeta";
import { APP_NAME } from "@/utils/constants";

const SECTIONS: { id: string; title: string; body: string[] }[] = [
  {
    id: "scope",
    title: "1. Scope",
    body: [
      `${APP_NAME} is a web-based employee management platform. It is designed to help organizations manage employee records, attendance, leave, departments, designations, reports, and internal office services such as amenity payments.`,
      `Except where expressly stated otherwise, ${APP_NAME} does not sell, ship, or deliver physical products to end users.`,
    ],
  },
  {
    id: "no-physical-shipping",
    title: "2. No Physical Shipping",
    body: [
      "The platform does not ship physical goods. You will not receive any physical packages, products, or merchandise from us or on our behalf.",
      `Any reference to "delivery" on ${APP_NAME} relates to electronic access to digital features and services, not to physical shipment.`,
    ],
  },
  {
    id: "digital-delivery",
    title: "3. Digital Delivery of Services",
    body: [
      `Employee/company services and digital features are delivered electronically through the platform over the internet. Access to these services is granted upon authentication to an authorized account within an organization that operates the platform.`,
      "No physical address, signature, or receipt of a shipped item is required to receive, use, or access the platform's features.",
      "Any notifications or reports you receive are provided electronically (for example, via email or in-platform messages).",
    ],
  },
  {
    id: "changes-to-this-policy",
    title: "4. Changes to This Policy",
    body: [
      "This Shipping Policy may be updated from time to time. The latest version will always be available on this page along with the effective date.",
    ],
  },
];

export function ShippingPolicyPage() {
  return (
    <PublicLayout>
      <PageMeta
        title={`${APP_NAME} | Shipping Policy`}
        description={`The shipping policy for ${APP_NAME}. EmpSphere is a digital employee management platform and does not ship physical products; services are delivered electronically.`}
      />

      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">
            Shipping Policy
          </h1>
          <p className="mt-3 text-sm text-slate-500">
            Effective date: 1 January 2026
          </p>
          <p className="mt-4 text-base text-slate-600">
            This page explains how EmpSphere delivers its services and why no
            physical shipping applies.
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
              For information about how we handle payments and refunds, please
              review our Cancellation & Refund Policy.
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
