import { currentPage, useEditor } from "./store";

/** Placeholder until the properties panel lands (M13). */
export function RightPanel() {
  const page = useEditor(currentPage);
  const selectedId = useEditor((s) => s.selectedId);
  const section = page?.sections.find((s) => s.id === selectedId);
  return (
    <aside className="min-h-0 overflow-y-auto border-l border-slate-200 bg-white p-4">
      {section ? (
        <>
          <h2 className="mb-2 text-sm font-semibold capitalize">{section.type}</h2>
          <pre className="whitespace-pre-wrap break-words rounded bg-slate-50 p-2 text-xs">
            {JSON.stringify({ variant: section.variant, style: section.style, props: section.props }, null, 2)}
          </pre>
        </>
      ) : (
        <p className="text-sm text-slate-500">Select a section in the list or in the preview.</p>
      )}
    </aside>
  );
}
