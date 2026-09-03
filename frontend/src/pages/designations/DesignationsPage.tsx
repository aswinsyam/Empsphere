/**
 * DesignationsPage.
 *
 * Allows authorized users to manage designations.
 */

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { designationService } from "@/services/designation.service";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { Loader } from "@/components/common/Loader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Pagination } from "@/components/common/Pagination";
import { Designation } from "@/types/designation";
import { canManageEmployees } from "@/utils/constants";
import { toastSuccess, toastApiError } from "@/components/common/ToastProvider";

const EMPTY_FORM = {
  name: "",
  code: "",
  description: "",
};

export function DesignationsPage() {
  const { user } = useAuth();
  const canManage = canManageEmployees(user?.role);

  const [designations, setDesignations] = useState<Designation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [search, setSearch] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Designation | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadDesignations = async (pageNum = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result = await designationService.list({
        search: search || undefined,
        page: pageNum,
        page_size: 10,
        include_inactive: true,
      });
      setDesignations(result.designations);
      setPage(result.page);
      setTotalPages(result.total_pages);
      setTotalRecords(result.total_records);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load designations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDesignations(1);
  }, [search]);

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (designation: Designation) => {
    setEditing(designation);
    setForm({
      name: designation.name,
      code: designation.code || "",
      description: designation.description || "",
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      if (editing) {
        await designationService.update(editing.designation_id, {
          name: form.name,
          code: form.code,
          description: form.description,
        });
        toastSuccess("Designation updated successfully.");
      } else {
        await designationService.create({
          name: form.name,
          code: form.code,
          description: form.description,
        });
        toastSuccess("Designation created successfully.");
      }
      setModalOpen(false);
      await loadDesignations(1);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setFormError(message);
      toastApiError(err, editing ? "Failed to update designation" : "Failed to create designation");
    } finally {
      setSubmitting(false);
    }
  };

  if (!canManage) {
    return (
      <div>
        <PageHeader title="Designations" subtitle="You do not have permission to manage designations." />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Designations"
        subtitle="Manage job designations and titles."
        actions={
          <Button onClick={openCreate}>New Designation</Button>
        }
      />

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : null}

      <div className="mb-4">
        <Input
          label="Search"
          name="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or code..."
          className="sm:max-w-xs"
        />
      </div>

      {loading && designations.length === 0 ? (
        <Loader />
      ) : designations.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-500">
          No designations found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Code</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Description</th>
                <th className="px-4 py-3 text-left font-medium text-slate-500">Status</th>
                <th className="px-4 py-3 text-right font-medium text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {designations.map((designation: Designation) => (
                <tr key={designation.designation_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{designation.name}</td>
                  <td className="px-4 py-3 text-slate-600">{designation.code || "-"}</td>
                  <td className="px-4 py-3 text-slate-600">{designation.description || "-"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={designation.is_active} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => openEdit(designation)}
                        className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                      >
                        Edit
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          totalRecords={totalRecords}
          onPageChange={(nextPage) => loadDesignations(nextPage)}
        />
      )}

      <Modal
        open={modalOpen}
        title={editing ? "Edit designation" : "New designation"}
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError ? (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{formError}</div>
          ) : null}

          <Input
            label="Name"
            name="name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />

          <Input
            label="Code (optional)"
            name="code"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
          />

          <Input
            label="Description (optional)"
            name="description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              {editing ? "Save changes" : "Create designation"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
