import { useState, type FormEvent } from "react";
import type { EditorMeta } from "@/api/types";
import { IconChevronRight, IconClose, IconPlus } from "@/components/icons";
import { AddSection } from "./AddSection";
import { BlogList } from "./blog/BlogList";
import { addPage, movePage, newId, removePage } from "./commands";
import { SectionList } from "./SectionList";
import { currentPage, useCanEditStructure, useEditor } from "./store";
import { t } from "@/i18n";

function PageList({ meta }: { meta: EditorMeta }) {
  const doc = useEditor((s) => s.doc)!;
  const pageId = useEditor((s) => s.pageId);
  const selectPage = useEditor((s) => s.selectPage);
  const apply = useEditor((s) => s.apply);
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const canEdit = useCanEditStructure();

  const [recipe, setRecipe] = useState("blank");
  const [drag, setDrag] = useState<{ id: string; over: number | null } | null>(null);

  const pick = (key: string) => {
    setRecipe(key);
    // suggest the recipe's name unless the person already typed their own
    if (!title.trim() || Object.values(meta.page_recipes).some((r) => r.title === title)) setTitle(meta.page_recipes[key].title);
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const id = newId("pg");
    apply(addPage(title.trim(), id, meta.page_recipes[recipe]?.sections ?? []));
    setRecipe("blank");
    selectPage(id);
    setTitle("");
    setAdding(false);
  };

  return (
    <div className="border-b border-ink-200 px-2 pb-2 pt-3">
      <div className="mb-1 flex items-center justify-between px-2">
        <h2 className="eyebrow-label">{t("Pages")}</h2>
        {canEdit && (
          <button aria-label={adding ? t("Cancel") : t("Add page")} title={adding ? t("Cancel") : t("Add page")} onClick={() => setAdding(!adding)}
            className="grid h-5 w-5 place-items-center rounded text-ink-500 transition hover:bg-ink-100 hover:text-ink-900">
            {adding ? <IconClose size={13} /> : <IconPlus size={13} />}
          </button>
        )}
      </div>
      {adding && (
        <form onSubmit={submit} className="mb-1 px-1">
          <input autoFocus aria-label={t("New page title")} value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder={t("Page title, then Enter")} className="field-input" />
          <div role="radiogroup" aria-label={t("Page layout")} className="mt-1.5 grid gap-1">
            {Object.entries(meta.page_recipes).map(([key, r]) => (
              <button key={key} type="button" role="radio" aria-checked={recipe === key} onClick={() => pick(key)}
                className={`rounded-md border px-2 py-1 text-start text-xs transition ${recipe === key ? "border-accent-600 bg-ink-50" : "border-ink-200 hover:border-ink-400"}`}>
                <span className="font-medium text-ink-900">{t(r.label)}</span>
                <span className="block text-[11px] text-ink-500">{t(r.description)}</span>
              </button>
            ))}
          </div>
        </form>
      )}
      <ul>
        {doc.pages.map((p, i) => {
          const on = p.id === pageId;
          return (
            <li key={p.id} draggable={canEdit && doc.pages.length > 1}
              onDragStart={(e) => { e.dataTransfer.effectAllowed = "move"; setDrag({ id: p.id, over: null }); }}
              onDragOver={(e) => { if (!drag) return; e.preventDefault(); if (drag.over !== i) setDrag({ ...drag, over: i }); }}
              onDrop={(e) => { e.preventDefault(); if (drag && drag.id !== p.id) apply(movePage(drag.id, i)); setDrag(null); }}
              onDragEnd={() => setDrag(null)}
              className={`group relative flex items-center ${drag?.id === p.id ? "opacity-40" : ""} ${drag && drag.over === i && drag.id !== p.id ? "border-t-2 border-accent-600" : ""}`}>
              <button onClick={() => selectPage(p.id)} aria-current={on ? "page" : undefined}
                className={`flex min-w-0 flex-1 items-baseline gap-2 rounded-md px-2 py-[5px] text-start text-[13px] transition ${on ? "bg-ink-100 font-medium text-ink-900" : "text-ink-700 hover:bg-ink-100/70"}`}>
                <span className="truncate">{p.title}</span>
                <span dir="ltr" className="truncate font-mono text-[10.5px] font-normal text-ink-400">/{p.slug}</span>
              </button>
              {canEdit && doc.pages.length > 1 && (
                <span className="absolute end-6 flex opacity-0 transition focus-within:opacity-100 group-hover:opacity-100">
                  <button aria-label={t("Move {name} up", { name: p.title })} title={t("Move up")} disabled={i === 0} onClick={() => apply(movePage(p.id, i - 1))}
                    className="grid h-5 w-5 place-items-center rounded text-ink-400 hover:bg-ink-200 hover:text-ink-900 disabled:opacity-25"><IconChevronRight size={12} className="-rotate-90" /></button>
                  <button aria-label={t("Move {name} down", { name: p.title })} title={t("Move down")} disabled={i === doc.pages.length - 1} onClick={() => apply(movePage(p.id, i + 1))}
                    className="grid h-5 w-5 place-items-center rounded text-ink-400 hover:bg-ink-200 hover:text-ink-900 disabled:opacity-25"><IconChevronRight size={12} className="rotate-90" /></button>
                </span>
              )}
              {canEdit && doc.pages.length > 1 && (
                <button aria-label={t("Delete page {name}", { name: p.title })} title={t("Delete page")}
                  className="absolute end-1 grid h-5 w-5 place-items-center rounded text-ink-400 opacity-0 transition hover:bg-red-600 hover:text-white focus:opacity-100 group-hover:opacity-100"
                  onClick={() => window.confirm(t("Delete the page \"{name}\" and its sections?", { name: p.title })) && apply(removePage(p.id))}>
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
    <div role="tablist" aria-label={t("Editor view")} className="flex gap-4 border-b border-ink-200 px-4">
      {(["site", "blog"] as const).map((v) => (
        <button key={v} role="tab" aria-selected={view === v} onClick={() => setView(v)}
          className={`-mb-px border-b-[1.5px] py-2.5 text-[13px] font-medium transition ${view === v ? "border-ink-900 text-ink-900" : "border-transparent text-ink-500 hover:text-ink-800"}`}>
          {v === "site" ? t("Pages") : t("Blog")}
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
      <div className="flex min-h-0 flex-col border-e border-ink-200 bg-white">
        <ViewTabs />
        <BlogList />
      </div>
    );
  return (
    <aside className="flex min-h-0 flex-col border-e border-ink-200 bg-white">
      <ViewTabs />
      <PageList meta={meta} />
      <div className="min-h-0 flex-1 overflow-y-auto px-2 py-3">
        <h2 className="eyebrow-label mb-1 px-2">{t("Sections")}</h2>
        {page && <SectionList sections={page.sections} meta={meta} />}
        {page?.sections.length === 0 && <p className="px-2 py-3 text-[13px] text-ink-500">{t("This page is empty. Add a section to begin.")}</p>}
        {canEdit && (
          <div className="mt-2 px-1">
            <AddSection meta={meta} />
          </div>
        )}
        {!canEdit && (
          <p className="mt-4 px-2 text-[12px] leading-relaxed text-ink-500">
            {t("You can edit the text, images and prices on this site. Layout and design are managed by your designer.")}
          </p>
        )}
      </div>
    </aside>
  );
}
