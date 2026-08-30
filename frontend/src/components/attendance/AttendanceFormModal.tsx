/**
 * AttendanceFormModal.
 *
 * Reusable modal for marking attendance.
 */

import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Employee } from "@/types/employee";

interface AttendanceFormModalProps {
  open: boolean;
  submitting: boolean;
  formError: string | null;
  employees: Employee[];
  selectedEmployee: string;
  form: {
    date: string;
    status: string;
    check_in: string;
    check_out: string;
    remarks: string;
  };
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  onFormChange: (field: string, value: string) => void;
  onEmployeeChange: (value: string) => void;
}

export function AttendanceFormModal({
  open,
  submitting,
  formError,
  employees,
  selectedEmployee,
  form,
  onClose,
  onSubmit,
  onFormChange,
  onEmployeeChange,
}: AttendanceFormModalProps) {
  return (
    <Modal open={open} title="Mark Attendance" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        {formError ? (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
        ) : null}

        <div>
          <label className="label" htmlFor="employee_id">
            Employee
          </label>
          <select
            id="employee_id"
            name="employee_id"
            value={selectedEmployee}
            onChange={(e) => onEmployeeChange(e.target.value)}
            className="input"
            required
          >
            <option value="">Select employee</option>
            {employees.map((emp: Employee) => (
              <option key={emp.user_id} value={emp.user_id}>
                {emp.first_name} {emp.last_name} ({emp.employee_code || emp.email})
              </option>
            ))}
          </select>
        </div>

        <Input
          label="Date"
          name="date"
          type="date"
          value={form.date}
          onChange={(e) => onFormChange("date", e.target.value)}
          required
        />

        <div>
          <label className="label" htmlFor="status">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={form.status}
            onChange={(e) => onFormChange("status", e.target.value)}
            className="input"
          >
            <option value="PRESENT">Present</option>
            <option value="ABSENT">Absent</option>
            <option value="HALF_DAY">Half Day</option>
            <option value="LEAVE">Leave</option>
          </select>
        </div>

        <Input
          label="Check In (optional)"
          name="check_in"
          type="time"
          value={form.check_in}
          onChange={(e) => onFormChange("check_in", e.target.value)}
        />

        <Input
          label="Check Out (optional)"
          name="check_out"
          type="time"
          value={form.check_out}
          onChange={(e) => onFormChange("check_out", e.target.value)}
        />

        <Input
          label="Remarks (optional)"
          name="remarks"
          value={form.remarks}
          onChange={(e) => onFormChange("remarks", e.target.value)}
        />

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            Mark Attendance
          </Button>
        </div>
      </form>
    </Modal>
  );
}
