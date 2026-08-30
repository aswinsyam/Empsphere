/**
 * PaymentsPage.
 *
 * Professional office payment management page.
 *
 * Layout:
 * - Payment History as main view
 * - "+ Make Payment" button opens modal
 * - Modal contains: Payment For -> Employee (optional) -> Amenity -> Amount -> Make Payment
 */

import { useEffect, useState, useCallback } from "react";
import { usePayment } from "@/hooks/usePayment";
import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { Modal } from "@/components/common/Modal";
import { formatDate } from "@/utils/helpers";
import { ROLES } from "@/utils/constants";
import { Payment, Amenity } from "@/types/payment";
import { paymentService } from "@/services/payment.service";
import { employeeService } from "@/services/employee.service";
import { departmentService } from "@/services/department.service";
import { Employee } from "@/types/employee";
import { Department } from "@/types/department";

type PaymentFor = "myself" | "employee";

export function PaymentsPage() {
  const {
    payments,
    amenities,
    total_records,
    total_pages,
    page,
    loading,
    amenitiesLoading,
    error,
    list,
    verify,
    cancel,
    loadMyPayments,
    loadAmenities,
  } = usePayment();
  const { user } = useAuth();

  const isEmployee = user?.role === ROLES.EMPLOYEE;
  const isSuperAdmin = user?.role === ROLES.SUPER_ADMIN;
  const canViewAll = Boolean(user?.role && user.role !== ROLES.EMPLOYEE);

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [paymentFor, setPaymentFor] = useState<PaymentFor>(isEmployee ? "myself" : "myself");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>("");
  const [selectedAmenity, setSelectedAmenity] = useState<Amenity | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<string | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [amenitiesError, setAmenitiesError] = useState<string | null>(null);

  const [filters, setFilters] = useState({
    employee_id: "",
    department_id: "",
    amenity_id: "",
    status: "",
    date: "",
  });

  // Load amenities and employee/department data on mount
  useEffect(() => {
    loadAmenitiesWrapper();
    if (canViewAll) {
      employeeService.list({ page_size: 100 }).then((res) => {
        setEmployees(res.employees || []);
      });
      departmentService.list({ page_size: 100 }).then((res) => {
        setDepartments(res.departments || []);
      });
    }
  }, [canViewAll, loadAmenities]);

  // Wrapper to handle amenities loading with error state
  const loadAmenitiesWrapper = async () => {
    try {
      setAmenitiesError(null);
      await loadAmenities();
    } catch (err) {
      setAmenitiesError("Failed to load amenities. Please try again.");
    }
  };

  // Load amenities when modal opens if not already loaded
  const ensureAmenitiesLoaded = async () => {
    if (amenities.length === 0 && !amenitiesLoading) {
      await loadAmenitiesWrapper();
    }
  };

  const loadData = useCallback(
    (pageNum = 1) => {
      if (isEmployee) {
        loadMyPayments({
          status: filters.status || undefined,
          date: filters.date || undefined,
          page: pageNum,
          page_size: 10,
        });
      } else {
        list({
          employee_id: filters.employee_id || undefined,
          department_id: filters.department_id || undefined,
          amenity_id: filters.amenity_id || undefined,
          status: filters.status || undefined,
          date: filters.date || undefined,
          page: pageNum,
          page_size: 10,
        });
      }
    },
    [isEmployee, filters, list, loadMyPayments]
  );

  useEffect(() => {
    loadData(1);
  }, [isEmployee, user?._id, filters.employee_id, filters.department_id, filters.amenity_id, filters.status, filters.date, loadData]);

  const openModal = async () => {
    setModalOpen(true);
    setFormError(null);
    setPaymentSuccess(null);
    setPaymentFor(isEmployee ? "myself" : "myself");
    setSelectedEmployeeId(isEmployee ? user?._id || "" : "");
    setSelectedAmenity(null);
    // Ensure amenities are loaded when modal opens
    await ensureAmenitiesLoaded();
  };

  const closeModal = () => {
    setModalOpen(false);
    setFormError(null);
    setPaymentFor("myself");
    setSelectedEmployeeId("");
    setSelectedAmenity(null);
  };

  const handleAmenityChange = (amenityId: string) => {
    const amenity = amenities.find((a) => a.amenity_id === amenityId);
    setSelectedAmenity(amenity || null);
  };

  const getSelectedEmployeeName = () => {
    if (paymentFor === "myself" || isEmployee) {
      return user?.full_name || "Myself";
    }
    const emp = employees.find((e) => e.user_id === selectedEmployeeId);
    return emp
      ? `${emp.full_name || emp.first_name + " " + emp.last_name} (${emp.employee_code})`
      : "Selected Employee";
  };

  const isFormValid = () => {
    if (paymentFor === "employee" && !selectedEmployeeId) {
      return false;
    }
    if (!selectedAmenity) {
      return false;
    }
    return true;
  };

  const loadCashfreeScript = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (document.querySelector('script[src="https://sdk.cashfree.com/js/v3/cashfree.js"]')) {
        resolve(true);
        return;
      }
      const script = document.createElement("script");
      script.src = "https://sdk.cashfree.com/js/v3/cashfree.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handlePaymentSuccess = async (
    paymentId: string,
    response: {
      gateway_order_id: string;
      gateway_payment_id: string;
      payment_status: string;
    }
  ) => {
    try {
      await verify(paymentId, response);
      setPaymentSuccess("Payment Successful");
      setTimeout(() => {
        closeModal();
        loadData(1);
      }, 1500);
    } catch (err) {
      setFormError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Payment verification failed."
      );
    }
  };

  const openCashfreeCheckout = async (orderData: {
    payment_id: string;
    order_id: string;
    payment_session_id: string;
    amount: number;
    currency: string;
  }) => {
    const scriptLoaded = await loadCashfreeScript();
    if (!scriptLoaded) {
      setFormError("Failed to load payment gateway. Please try again.");
      return;
    }

    const cashfree = (window as any).Cashfree({
      mode: "sandbox",
    });

    cashfree
      .checkout({
        paymentSessionId: orderData.payment_session_id,
        redirectTarget: "_modal",
      })
      .then((result: any) => {
        if (result.error) {
          setFormError("Payment was cancelled or failed. Please try again.");
          return;
        }
        if (result.paymentDetails) {
          handlePaymentSuccess(orderData.payment_id, {
            gateway_order_id: orderData.order_id,
            gateway_payment_id: result.paymentDetails.cfPaymentId || "",
            payment_status: result.paymentDetails.paymentStatus || "",
          });
        }
      })
      .catch((err: any) => {
        setFormError(
          err && typeof err === "object" && "message" in err
            ? String((err as { message: string }).message)
            : "Payment failed. Please try again."
        );
      });
  };

  const handleMakePayment = async () => {
    if (!isFormValid()) {
      setFormError("Please fill in all required fields.");
      return;
    }

    const employeeId = isEmployee || paymentFor === "myself" ? user?._id || "" : selectedEmployeeId;

    setFormError(null);
    setSubmitting(true);

    try {
      const result = await paymentService.create({
        employee_id: employeeId,
        amenity_id: selectedAmenity!.amenity_id,
      });
      await openCashfreeCheckout(result);
    } catch (err) {
      setFormError(
        err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Something went wrong."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (payment: Payment) => {
    if (!window.confirm(`Cancel payment for "${payment.amenity_name}"?`)) return;
    try {
      await cancel(payment.payment_id);
      loadData(page);
    } catch {
      // handled by slice
    }
  };

  const clearFilters = () => {
    setFilters({ employee_id: "", department_id: "", amenity_id: "", status: "", date: "" });
  };

  const openDetailModal = (payment: Payment) => {
    setSelectedPayment(payment);
    setDetailModalOpen(true);
  };

  const getEmployeeName = (employeeId: string) => {
    const emp = employees.find((e) => e.user_id === employeeId);
    return emp
      ? `${emp.full_name || emp.first_name + " " + emp.last_name} (${emp.employee_code})`
      : employeeId;
  };

  const getDepartmentName = (departmentId: string) => {
    const dept = departments.find((d) => d.department_id === departmentId);
    return dept ? dept.name : "";
  };

  return (
    <div>
      <PageHeader
        title="Payments"
        subtitle="View payment history and make office amenity payments."
        actions={
          <Button onClick={openModal}>+ Make Payment</Button>
        }
      />

      {(error || formError) && !modalOpen && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error || formError}
        </div>
      )}

      {/* Filters for HR/Admin/SuperAdmin */}
      {canViewAll && (
        <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="min-w-[150px]">
              <label className="label">Employee</label>
              <select
                value={filters.employee_id}
                onChange={(e) => setFilters({ ...filters, employee_id: e.target.value })}
                className="input"
              >
                <option value="">All Employees</option>
                {employees.map((emp) => (
                  <option key={emp.user_id} value={emp.user_id}>
                    {emp.full_name || emp.first_name + " " + emp.last_name} ({emp.employee_code})
                  </option>
                ))}
              </select>
            </div>
            <div className="min-w-[150px]">
              <label className="label">Department</label>
              <select
                value={filters.department_id}
                onChange={(e) => setFilters({ ...filters, department_id: e.target.value })}
                className="input"
              >
                <option value="">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept.department_id} value={dept.department_id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="min-w-[150px]">
              <label className="label">Amenity</label>
              <select
                value={filters.amenity_id}
                onChange={(e) => setFilters({ ...filters, amenity_id: e.target.value })}
                className="input"
              >
                <option value="">All Amenities</option>
                {amenities.map((amenity) => (
                  <option key={amenity.amenity_id} value={amenity.amenity_id}>
                    {amenity.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="min-w-[150px]">
              <label className="label">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="input"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="PAID">Paid</option>
                <option value="FAILED">Failed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
            <div className="min-w-[150px]">
              <label className="label">Date</label>
              <input
                type="date"
                value={filters.date}
                onChange={(e) => setFilters({ ...filters, date: e.target.value })}
                className="input"
              />
            </div>
            <button onClick={clearFilters} className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium">
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Filters for Employee */}
      {isEmployee && (
        <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="min-w-[150px]">
              <label className="label">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="input"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="PAID">Paid</option>
                <option value="FAILED">Failed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
            <div className="min-w-[150px]">
              <label className="label">Date</label>
              <input
                type="date"
                value={filters.date}
                onChange={(e) => setFilters({ ...filters, date: e.target.value })}
                className="input"
              />
            </div>
            <button onClick={clearFilters} className="btn-ghost rounded-lg px-4 py-2 text-sm font-medium">
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Payment History Table */}
      {loading && payments.length === 0 ? (
        <Loader />
      ) : payments.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          No payment records found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                {canViewAll && (
                  <>
                    <th className="px-4 py-3 text-left font-medium text-slate-500">Employee</th>
                    <th className="px-4 py-3 text-left font-medium text-slate-500">Department</th>
                  </>
                )}
                <th className="px-4 py-3 text-left font-medium text-slate-500">Amenity</th>
                <th className="px-4 py-3 text-right font-medium text-slate-500">Amount</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Date</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Reference</th>
                <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payments.map((payment) => (
                <tr
                  key={payment.payment_id}
                  className="hover:bg-slate-50 cursor-pointer"
                  onClick={() => openDetailModal(payment)}
                >
                  {canViewAll && (
                    <>
                      <td className="px-4 py-3 text-slate-600">{getEmployeeName(payment.employee_id)}</td>
                      <td className="px-4 py-3 text-slate-600">
                        {getDepartmentName(
                          employees.find((e) => e.user_id === payment.employee_id)?.department_id || ""
                        )}
                      </td>
                    </>
                  )}
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-900">{payment.amenity_name}</div>
                  </td>
                  <td className="px-4 py-3 text-right font-medium text-slate-900">
                    Rs.{payment.amount.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDate(payment.created_at || payment.payment_date)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={payment.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {payment.gateway_payment_id
                      ? payment.gateway_payment_id.slice(0, 12) + "..."
                      : "-"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      {payment.status === "PENDING" &&
                        (isEmployee ? payment.employee_id === user?._id : true) && (
                          <button
                            onClick={() => handleCancel(payment)}
                            className="rounded border border-red-200 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-50"
                          >
                            Cancel
                          </button>
                        )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={total_pages}
          totalRecords={total_records}
          onPageChange={(nextPage) => loadData(nextPage)}
        />
      )}

      {/* Make Payment Modal */}
      <Modal open={modalOpen} title="Make Payment" onClose={closeModal}>
        <div className="space-y-5">
          {formError && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
          )}

          {paymentSuccess && (
            <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">{paymentSuccess}</div>
          )}

          {/* Step 1: Payment For */}
          {!isEmployee && (
            <div>
              <label className="label">Payment For</label>
              <div className="flex gap-2">
                {!isSuperAdmin && (
                  <button
                    type="button"
                    onClick={() => setPaymentFor("myself")}
                    className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition ${
                      paymentFor === "myself"
                        ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                        : "border-slate-200 text-slate-600 hover:border-slate-300"
                    }`}
                  >
                    Myself
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setPaymentFor("employee")}
                  className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition ${
                    paymentFor === "employee"
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  Select Employee
                </button>
              </div>
            </div>
          )}

          {/* Show selected employee info for self-payment */}
          {(isEmployee || paymentFor === "myself") && (
            <div>
              <label className="label">Payment For</label>
              <div className="rounded-lg bg-slate-50 p-3">
                <div className="font-medium text-slate-900">{user?.full_name}</div>
                <div className="text-sm text-slate-500">{user?.email}</div>
              </div>
            </div>
          )}

          {/* Step 2: Select Employee (if applicable) */}
          {paymentFor === "employee" && (
            <div>
              <label className="label">Select Employee</label>
              <select
                value={selectedEmployeeId}
                onChange={(e) => setSelectedEmployeeId(e.target.value)}
                className="input"
              >
                <option value="">Choose an employee...</option>
                {employees.map((emp) => (
                  <option key={emp.user_id} value={emp.user_id}>
                    {emp.full_name || emp.first_name + " " + emp.last_name} ({emp.employee_code})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Step 3: Select Amenity */}
          <div>
            <label className="label">Select Amenity</label>
            {amenitiesLoading ? (
              <div className="flex items-center gap-2 rounded-lg border border-slate-200 p-3 text-sm text-slate-500">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
                Loading amenities...
              </div>
            ) : amenitiesError ? (
              <div className="space-y-2">
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{amenitiesError}</div>
                <Button variant="ghost" onClick={loadAmenitiesWrapper}>
                  Retry
                </Button>
              </div>
            ) : amenities.length === 0 ? (
              <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
                No amenities available. Please contact an administrator.
              </div>
            ) : (
              <select
                value={selectedAmenity?.amenity_id || ""}
                onChange={(e) => handleAmenityChange(e.target.value)}
                className="input"
              >
                <option value="">Choose an amenity...</option>
                {amenities.map((amenity) => (
                  <option key={amenity.amenity_id} value={amenity.amenity_id}>
                    {amenity.name} - Rs.{amenity.amount.toFixed(2)}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Amount Display */}
          {selectedAmenity && (
            <div>
              <label className="label">Amount</label>
              <div className="rounded-lg bg-slate-50 p-4">
                <div className="text-2xl font-semibold text-indigo-600">
                  Rs.{selectedAmenity.amount.toFixed(2)}
                </div>
                {selectedAmenity.description && (
                  <div className="mt-1 text-sm text-slate-500">{selectedAmenity.description}</div>
                )}
              </div>
            </div>
          )}

          {/* Summary */}
          {selectedAmenity && (
            <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
              <strong>Payment Summary:</strong>
              <div className="mt-1">
                Paying <strong>Rs.{selectedAmenity.amount.toFixed(2)}</strong> for{" "}
                <strong>{selectedAmenity.name}</strong>
                {paymentFor === "employee" && selectedEmployeeId && (
                  <> for <strong>{getSelectedEmployeeName()}</strong></>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              onClick={handleMakePayment}
              loading={submitting}
              disabled={!isFormValid() || submitting || !!paymentSuccess}
            >
              Make Payment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Payment Details Modal */}
      <Modal open={detailModalOpen} title="Payment Details" onClose={() => setDetailModalOpen(false)}>
        {selectedPayment && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Employee</label>
                <div className="text-sm text-slate-900">{getEmployeeName(selectedPayment.employee_id)}</div>
              </div>
              <div>
                <label className="label">Department</label>
                <div className="text-sm text-slate-900">
                  {getDepartmentName(
                    employees.find((e) => e.user_id === selectedPayment.employee_id)?.department_id || ""
                  )}
                </div>
              </div>
              <div>
                <label className="label">Amenity</label>
                <div className="text-sm text-slate-900">{selectedPayment.amenity_name}</div>
              </div>
              <div>
                <label className="label">Amount</label>
                <div className="text-sm font-semibold text-slate-900">Rs.{selectedPayment.amount.toFixed(2)}</div>
              </div>
              <div>
                <label className="label">Payment Date</label>
                <div className="text-sm text-slate-900">
                  {formatDate(selectedPayment.payment_date || selectedPayment.created_at)}
                </div>
              </div>
              <div>
                <label className="label">Status</label>
                <StatusBadge status={selectedPayment.status} />
              </div>
              <div>
                <label className="label">Payment Reference</label>
                <div className="text-sm text-slate-900 font-mono">{selectedPayment.gateway_payment_id || "-"}</div>
              </div>
              <div>
                <label className="label">Order ID</label>
                <div className="text-sm text-slate-900 font-mono">{selectedPayment.gateway_order_id || "-"}</div>
              </div>
            </div>
            <div className="flex justify-end pt-2">
              <Button variant="ghost" onClick={() => setDetailModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
