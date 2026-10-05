import { useState, type FormEvent } from "react";
import type { EditorMeta } from "@/api/types";
import { IconClose, IconPlus } from "@/components/icons";
import { AddSection } from "./AddSection";
import { BlogList } from "./blog/BlogList";
import { addPage, newId, removePage } from "./commands";
import { SectionList } from "./SectionList";
import { currentPage, useCanEditStructure, useEditor } from "./store";

function PageList() {
  const doc = useEditor((s) => s.doc)!;
  const pageId = useEditor((s) => s.pageId);
  const selectPage = useEditor((s) => s.selectPage);
  const apply = useEditor((s) => s.apply);
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const canEdit = useCanEditStructure();

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
    <div className="border-b border-ink-200 px-2 pb-2 pt-3">
      <div className="mb-1 flex items-center justify-between px-2">
        <h2 className="eyebrow-label">Pages</h2>
        {canEdit && (
          <button aria-label={adding ? "Cancel" : "Add page"} title={adding ? "Cancel" : "Add page"} onClick={() => setAdding(!adding)}
            className="grid h-5 w-5 place-items-center rounded text-ink-500 transition hover:bg-ink-100 hover:text-ink-900">
            {adding ? <IconClose size={13} /> : <IconPlus size={13} />}
          </button>
        )}
      </div>
      {adding && (
        <form onSubmit={submit} className="mb-1 px-1">
          <input autoFocus aria-label="New page title" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Page title, then Enter" className="field-input" />
        </form>
      )}
      <ul>
        {doc.pages.map((p) => {
          const on = p.id === pageId;
          return (
            <li key={p.id} className="group relative flex items-center">
              <button onClick={() => selectPage(p.id)} aria-current={on ? "page" : undefined}
                className={`flex min-w-0 flex-1 items-baseline gap-2 rounded-md px-2 py-[5px] text-left text-[13px] transition ${on ? "bg-ink-100 font-medium text-ink-900" : "text-ink-700 hover:bg-ink-100/70"}`}>
                <span className="truncate">{p.title}</span>
                <span className="truncate font-mono text-[10.5px] font-normal text-ink-400">/{p.slug}</span>
              </button>
              {canEdit && doc.pages.length > 1 && (
                <button aria-label={`Delete page ${p.title}`} title="Delete page"
                  className="absolute right-1 grid h-5 w-5 place-items-center rounded text-ink-400 opacity-0 transition hover:bg-red-600 hover:text-white focus:opacity-100 group-hover:opacity-100"
                  onClick={() => window.confirm(`Delete the page "${p.title}" and its sections?`) && apply(removePage(p.id))}>
                  <IconClose size={12} />
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function ViewTabs() {
  const view = useEditor((s) => s.view);
  const setView = useEditor((s) => s.setView);
  return (
    <div role="tablist" aria-label="Editor view" className="flex gap-4 border-b border-ink-200 px-4">
      {(["site", "blog"] as const).map((v) => (
        <button key={v} role="tab" aria-selected={view === v} onClick={() => setView(v)}
          className={`-mb-px border-b-[1.5px] py-2.5 text-[13px] font-medium transition ${view === v ? "border-ink-900 text-ink-900" : "border-transparent text-ink-500 hover:text-ink-800"}`}>
          {v === "site" ? "Pages" : "Blog"}
        </button>
      ))}
    </div>
  );
}

export function LeftRail({ meta }: { meta: EditorMeta }) {
  const page = useEditor(currentPage);
  const view = useEditor((s) => s.view);
  const canEdit = useCanEditStructure();
  if (view === "blog")
    return (
      <div className="flex min-h-0 flex-col border-r border-ink-200 bg-white">
        <ViewTabs />
        <BlogList />
      </div>
    );
  return (
    <aside className="flex min-h-0 flex-col border-r border-ink-200 bg-white">
      <ViewTabs />
      <PageList />
      <div className="min-h-0 flex-1 overflow-y-auto px-2 py-3">
        <h2 className="eyebrow-label mb-1 px-2">Sections</h2>
        {page && <SectionList sections={page.sections} meta={meta} />}
        {page?.sections.length === 0 && <p className="px-2 py-3 text-[13px] text-ink-500">This page is empty. Add a section to begin.</p>}
        {canEdit && (
          <div className="mt-2 px-1">
            <AddSection meta={meta} />
          </div>
        )}
        {!canEdit && (
          <p className="mt-4 px-2 text-[12px] leading-relaxed text-ink-500">
            You can edit the text, images and prices on this site. Layout and design are managed by your designer.
          </p>
        )}
      </div>
    </aside>
  );
}
