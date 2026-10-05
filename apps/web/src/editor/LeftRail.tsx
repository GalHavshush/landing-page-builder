import { useState, type FormEvent } from "react";
import type { EditorMeta } from "@/api/types";
import { AddSection } from "./AddSection";
import { addPage, newId, removePage } from "./commands";
import { BlogList } from "./blog/BlogList";
import { SectionList } from "./SectionList";
import { currentPage, useEditor } from "./store";

function PageList() {
  const doc = useEditor((s) => s.doc)!;
  const pageId = useEditor((s) => s.pageId);
  const selectPage = useEditor((s) => s.selectPage);
  const apply = useEditor((s) => s.apply);
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const id = newId("pg");
    apply(addPage(title.trim(), id));
    selectPage(id);
    setTitle("");
    setAdding(false);
  };

  return (
    <div className="border-b border-slate-200 p-3">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Pages</h2>
        <button className="text-xs text-indigo-600 hover:underline" onClick={() => setAdding(!adding)}>
          {adding ? "Cancel" : "+ Add page"}
        </button>
      </div>
      {adding && (
        <form onSubmit={submit} className="mb-2">
          <input
            autoFocus
            aria-label="New page title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Page title, then Enter"
            className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm"
          />
        </form>
      )}
      <ul className="space-y-0.5">
        {doc.pages.map((p) => (
          <li key={p.id} className="group flex items-center">
            <button
              onClick={() => selectPage(p.id)}
              className={`min-w-0 flex-1 truncate rounded-md px-2.5 py-1.5 text-left text-sm ${
                p.id === pageId ? "bg-indigo-50 font-medium text-indigo-700" : "text-slate-700 hover:bg-slate-100"
              }`}
            >
              {p.title}
              <span className="ml-2 text-xs text-slate-400">/{p.slug}</span>
            </button>
            {doc.pages.length > 1 && (
              <button
                aria-label={`Delete page ${p.title}`}
                title="Delete page"
                className="px-1.5 text-slate-400 opacity-0 hover:text-red-600 group-hover:opacity-100 focus:opacity-100"
                onClick={() => window.confirm(`Delete the page "${p.title}" and its sections?`) && apply(removePage(p.id))}
              >
                ✕
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ViewTabs() {
  const view = useEditor((s) => s.view);
  const setView = useEditor((s) => s.setView);
  return (
    <div role="tablist" aria-label="Editor view" className="grid grid-cols-2 border-b border-slate-200 bg-white text-sm">
      {(["site", "blog"] as const).map((v) => (
        <button key={v} role="tab" aria-selected={view === v} onClick={() => setView(v)}
          className={`py-2 capitalize ${view === v ? "border-b-2 border-indigo-600 font-medium text-indigo-700" : "text-slate-500 hover:text-slate-800"}`}>
          {v === "site" ? "Pages" : "Blog"}
        </button>
      ))}
    </div>
  );
}

export function LeftRail({ meta }: { meta: EditorMeta }) {
  const page = useEditor(currentPage);
  const view = useEditor((s) => s.view);
  if (view === "blog")
    return (
      <div className="flex min-h-0 flex-col border-r border-slate-200 bg-white">
        <ViewTabs />
        <BlogList />
      </div>
    );
  return (
    <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-white">
      <ViewTabs />
      <PageList />
      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Sections</h2>
        {page && <SectionList sections={page.sections} meta={meta} />}
        {page?.sections.length === 0 && <p className="mb-2 text-sm text-slate-500">This page is empty.</p>}
        <div className="mt-3">
          <AddSection meta={meta} />
        </div>
      </div>
    </aside>
  );
}
