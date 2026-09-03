/**
 * Pagination.
 *
 * Reusable pagination control for server-side paginated lists.
 * Displays the current page range and provides Previous / Next buttons.
 */

import { Button } from "@/components/common/Button";

interface PaginationProps {
  /** Current page number (1-based). */
  page: number;
  /** Total number of pages. */
  totalPages: number;
  /** Total number of records across all pages. */
  totalRecords: number;
  /** Called when the user requests a different page. */
  onPageChange: (page: number) => void;
}

export function Pagination({
  page,
  totalPages,
  totalRecords,
  onPageChange,
}: PaginationProps) {
  return (
    <div className="mt-4 flex items-center justify-between">
      <p className="text-sm text-slate-500">
        Page {page} of {totalPages} ({totalRecords} total)
      </p>
      <div className="flex gap-2">
        <Button
          variant="ghost"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </Button>
        <Button
          variant="ghost"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
