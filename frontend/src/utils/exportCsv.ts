/**
 * CSV export utility.
 *
 * Converts structured data into a CSV file and triggers a browser download.
 * Handles commas, quotes, and newlines safely by wrapping fields in quotes
 * when necessary.
 */

/**
 * Escape a single CSV field.
 *
 * If the field contains a comma, quote, or newline, wrap it in double quotes
 * and escape any existing double quotes by doubling them.
 * This follows RFC 4180 so Excel and other spreadsheet tools parse it correctly.
 */
function escapeCsvField(value: string): string {
  const text = String(value ?? "");
  if (text.includes(",") || text.includes('"') || text.includes("\n") || text.includes("\r")) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

/**
 * Convert headers and rows into a CSV string.
 *
 * @param headers - Column headers (first row).
 * @param rows - Data rows. Each row must match the headers length.
 */
export function toCsv(headers: string[], rows: string[][]): string {
  const lines: string[] = [];
  lines.push(headers.map(escapeCsvField).join(","));
  for (const row of rows) {
    lines.push(row.map(escapeCsvField).join(","));
  }
  return lines.join("\n");
}

/**
 * Download CSV data as a file in the browser.
 *
 * @param filename - Name of the downloaded file (e.g. `leaves.csv`).
 * @param csvContent - Raw CSV string content.
 */
export function downloadCsv(filename: string, csvContent: string): void {
  // Create a Blob with MIME type text/csv so the browser treats it as a spreadsheet.
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  // Create a temporary invisible link to trigger the download.
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();

  // Clean up the object URL and temporary link after the download starts.
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export an array of objects as a CSV file.
 *
 * @param filename - Downloaded file name.
 * @param data - Array of objects to export.
 * @param columns - Array of `{ header, key }` mappings.
 */
export function exportObjectsToCsv(
  filename: string,
  data: unknown[],
  columns: { header: string; key: string }[]
): void {
  if (!data.length) {
    return;
  }

  const headers = columns.map((col) => col.header);
  const rows = data.map((item) =>
    columns.map((col) => {
      const value = (item as Record<string, unknown>)[col.key];
      if (value === null || value === undefined) {
        return "";
      }
      if (value instanceof Date) {
        return value.toISOString();
      }
      return String(value);
    })
  );

  const csv = toCsv(headers, rows);
  downloadCsv(filename, csv);
}
