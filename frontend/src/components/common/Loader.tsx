/**
 * Loader.
 * A simple centered spinner used while content is loading.
 */

interface LoaderProps {
  text?: string;
}

export function Loader({ text = "Loading..." }: LoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div
        className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent"
        role="status"
        aria-label="Loading"
      />
      {text ? <p className="text-sm text-slate-500">{text}</p> : null}
    </div>
  );
}
