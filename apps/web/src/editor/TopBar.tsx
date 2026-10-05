import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/api/client";
import type { EditorMeta, Project } from "@/api/types";
import { IconBack, IconDesktop, IconEye, IconMobile, IconRedo, IconSettings, IconUndo } from "@/components/icons";
import { LivePreview } from "@/components/LivePreview";
import { Button } from "@/components/ui";
import { ExportDialog } from "./ExportDialog";
import { ShareDialog } from "./ShareDialog";
import { useEditor, type SaveStatus } from "./store";
import { t } from "@/i18n";

const STATUS: Record<SaveStatus, { text: string; dot: string }> = {
  saved: { text: "Saved", dot: "bg-emerald-700" },
  dirty: { text: "Editing", dot: "bg-ink-400" },
  saving: { text: "Saving", dot: "bg-accent-500 animate-pulse" },
  error: { text: "Offline, retrying", dot: "bg-accent-500" },
  invalid: { text: "Can't save", dot: "bg-red-600" },
  conflict: { text: "Out of date", dot: "bg-red-600" },
};

function SaveIndicator() {
  const status = useEditor((s) => s.saveStatus);
  const s = STATUS[status];
  return (
    <span role="status" className="flex items-center gap-1.5 text-[12px] text-ink-500">
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {t(s.text)}
    </span>
  );
}

const iconBtn =
  "grid h-7 w-7 place-items-center rounded-md text-ink-600 transition hover:bg-ink-100 hover:text-ink-900 disabled:pointer-events-none disabled:opacity-30";

export function TopBar({ project, meta }: { project: Project; meta: EditorMeta }) {
  const device = useEditor((s) => s.device);
  const setDevice = useEditor((s) => s.setDevice);
  const doc = useEditor((s) => s.doc)!;
  const lang = useEditor((s) => s.lang);
  const setLang = useEditor((s) => s.setLang);
  const canUndo = useEditor((s) => s.undoStack.length > 0);
  const canRedo = useEditor((s) => s.redoStack.length > 0);
  const undo = useEditor((s) => s.undo);
  const redo = useEditor((s) => s.redo);
  // the preview shows the document as it is when opened, saved or not
  const [live, setLive] = useState<{ doc: typeof doc; page: string; lang: string } | null>(null);
  const openLive = () => {
    const s = useEditor.getState();
    if (s.doc && s.pageId) setLive({ doc: s.doc, page: s.pageId, lang: s.lang ?? s.doc.site.default_language });
  };

  return (
    <header className="grid h-11 grid-cols-[1fr_auto_1fr] items-center border-b border-ink-200 bg-white px-3">
      <div className="flex min-w-0 items-center gap-1">
        <Link to="/" aria-label={t("All sites")} title={t("All sites")} className={iconBtn}>
          <IconBack size={15} />
        </Link>
        <span className="mx-1 h-4 w-px bg-ink-200" />
        <h1 className="truncate px-1 text-[13px] font-semibold tracking-tight">{project.name}</h1>
        <span className="mx-1 h-4 w-px bg-ink-200" />
        <button aria-label={t("Undo")} title={`${t("Undo")}  Ctrl+Z`} disabled={!canUndo} onClick={undo} className={iconBtn}><IconUndo size={15} /></button>
        <button aria-label={t("Redo")} title={`${t("Redo")}  Ctrl+Shift+Z`} disabled={!canRedo} onClick={redo} className={iconBtn}><IconRedo size={15} /></button>
        <span className="ms-2"><SaveIndicator /></span>
      </div>

      <div className="flex items-center gap-2">
        {doc.site.languages.length > 1 && (
          <select aria-label={t("Language")} value={lang ?? ""} onChange={(e) => setLang(e.target.value)}
            className="h-7 rounded-md border border-ink-300 bg-white px-2 text-[12px] font-medium">
            {doc.site.languages.map((l) => (
              <option key={l} value={l}>{meta.languages[l] ?? l}</option>
            ))}
          </select>
        )}
        <div className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200" role="group" aria-label={t("Preview size")}>
          {(["desktop", "mobile"] as const).map((d) => (
            <button key={d} onClick={() => setDevice(d)} aria-pressed={device === d} aria-label={d === "desktop" ? t("Desktop") : t("Mobile")} title={d === "desktop" ? t("Desktop") : t("Mobile")}
              className={`grid h-6 w-8 place-items-center rounded-[5px] transition ${device === d ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-500 hover:text-ink-900"}`}>
              {d === "desktop" ? <IconDesktop size={14} /> : <IconMobile size={14} />}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-end gap-2">
        {project.role === "editor" && <span className="rounded bg-accent-50 px-2 py-0.5 text-[11px] font-medium text-accent-700">{t("Content editing")}</span>}
        <Button variant="ghost" onClick={openLive}><IconEye size={14} />{t("Preview")}</Button>
        <Link to="/settings" aria-label={t("Settings")} title={t("Settings")} className={iconBtn}><IconSettings size={15} /></Link>
        {project.role === "owner" && <ShareDialog projectId={project.id} />}
        <ExportDialog projectId={project.id} />
      </div>
      {live && (
        <LivePreview title={project.name} onClose={() => setLive(null)}
          load={async (to, signal) =>
            (await api<{ html: string }>(`/projects/${project.id}/preview`, {
              method: "POST", signal,
              body: { doc: live.doc, page_id: to.page ?? live.page, lang: to.lang ?? live.lang, interactive: true },
            })).html}
        />
      )}
    </header>
  );
}
