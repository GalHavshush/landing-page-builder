import { Link } from "react-router-dom";
import { api } from "@/api/client";
import type { EditorMeta, Project } from "@/api/types";
import { Button } from "@/components/ui";
import { saver } from "./saving";
import { useEditor, type SaveStatus } from "./store";

async function downloadExport(projectId: number, slug: string) {
  await saver.current?.flush(); // export what the user sees, not the last autosave
  const res = await api<Response>(`/projects/${projectId}/export`, { method: "POST", raw: true });
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = `${slug}.zip`;
  a.click();
  URL.revokeObjectURL(url);
}

const STATUS: Record<SaveStatus, { text: string; cls: string }> = {
  saved: { text: "All changes saved", cls: "text-slate-500" },
  dirty: { text: "Unsaved changes…", cls: "text-slate-500" },
  saving: { text: "Saving…", cls: "text-slate-500" },
  error: { text: "Offline? Retrying…", cls: "text-amber-600" },
  invalid: { text: "Can't save these changes", cls: "text-red-600" },
  conflict: { text: "Out of date", cls: "text-red-600" },
};

function SaveIndicator() {
  const status = useEditor((s) => s.saveStatus);
  return (
    <span role="status" className={`text-xs ${STATUS[status].cls}`}>
      {STATUS[status].text}
    </span>
  );
}

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

  return (
    <header className="flex h-13 items-center justify-between border-b border-slate-200 bg-white px-4">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-sm text-slate-500 hover:text-slate-800">
          ← Sites
        </Link>
        <h1 className="text-sm font-semibold">{project.name}</h1>
        <div className="ml-2 flex gap-1">
          <button aria-label="Undo" title="Undo (Ctrl+Z)" disabled={!canUndo} onClick={undo}
            className="rounded px-2 py-1 text-slate-600 hover:bg-slate-100 disabled:opacity-30">↶</button>
          <button aria-label="Redo" title="Redo (Ctrl+Shift+Z)" disabled={!canRedo} onClick={redo}
            className="rounded px-2 py-1 text-slate-600 hover:bg-slate-100 disabled:opacity-30">↷</button>
        </div>
        <SaveIndicator />
      </div>
      <div className="flex items-center gap-3">
        {doc.site.languages.length > 1 && (
          <select aria-label="Language" value={lang ?? ""} onChange={(e) => setLang(e.target.value)}
            className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm">
            {doc.site.languages.map((l) => (
              <option key={l} value={l}>{meta.languages[l] ?? l}</option>
            ))}
          </select>
        )}
        <div className="inline-flex overflow-hidden rounded-md border border-slate-300 text-sm" role="group" aria-label="Preview size">
          {(["desktop", "mobile"] as const).map((d) => (
            <button key={d} onClick={() => setDevice(d)} aria-pressed={device === d}
              className={`px-3 py-1 capitalize ${device === d ? "bg-slate-900 text-white" : "bg-white text-slate-600 hover:bg-slate-50"}`}>
              {d}
            </button>
          ))}
        </div>
        <Button variant="ghost" onClick={() => downloadExport(project.id, project.slug)}>Export ZIP</Button>
      </div>
    </header>
  );
}
