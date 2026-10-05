import type { EditorMeta, Section } from "@/api/types";
import { currentPage, useEditor } from "./store";

function sectionSubtitle(s: Section): string {
  const p = s.props as unknown as Record<string, unknown>;
  const text = (p.heading as string) || (p.eyebrow as string) || "";
  return text.slice(0, 40);
}

export function LeftRail({ meta }: { meta: EditorMeta }) {
  const doc = useEditor((s) => s.doc)!;
  const pageId = useEditor((s) => s.pageId);
  const selectedId = useEditor((s) => s.selectedId);
  const selectPage = useEditor((s) => s.selectPage);
  const selectSection = useEditor((s) => s.selectSection);
  const page = useEditor(currentPage);
  const label = (type: string) => meta.sections.find((m) => m.type === type)?.label ?? type;

  return (
    <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-3">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Pages</h2>
        <ul className="space-y-0.5">
          {doc.pages.map((p) => (
            <li key={p.id}>
              <button
                onClick={() => selectPage(p.id)}
                className={`w-full rounded-md px-2.5 py-1.5 text-left text-sm ${
                  p.id === pageId ? "bg-indigo-50 font-medium text-indigo-700" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                {p.title}
                <span className="ml-2 text-xs text-slate-400">/{p.slug}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Sections</h2>
        <ul className="space-y-1">
          {page?.sections.map((s) => (
            <li key={s.id}>
              <button
                onClick={() => selectSection(s.id)}
                className={`w-full rounded-md border px-2.5 py-2 text-left ${
                  s.id === selectedId ? "border-indigo-400 bg-indigo-50" : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="text-sm font-medium">{label(s.type)}</div>
                <div className="truncate text-xs text-slate-500">{sectionSubtitle(s) || "—"}</div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
