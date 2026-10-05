import { Link } from "react-router-dom";
import { api } from "@/api/client";
import type { EditorMeta, Project } from "@/api/types";
import { Button } from "@/components/ui";
import { useEditor } from "./store";

async function downloadExport(projectId: number, slug: string) {
  const res = await api<Response>(`/projects/${projectId}/export`, { method: "POST", raw: true });
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = `${slug}.zip`;
  a.click();
  URL.revokeObjectURL(url);
}

export function TopBar({ project, meta }: { project: Project; meta: EditorMeta }) {
  const device = useEditor((s) => s.device);
  const setDevice = useEditor((s) => s.setDevice);
  const doc = useEditor((s) => s.doc)!;
  const lang = useEditor((s) => s.lang);
  const setLang = useEditor((s) => s.setLang);

  return (
    <header className="flex h-13 items-center justify-between border-b border-slate-200 bg-white px-4">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-sm text-slate-500 hover:text-slate-800">
          ← Sites
        </Link>
        <h1 className="text-sm font-semibold">{project.name}</h1>
      </div>
      <div className="flex items-center gap-3">
        {doc.site.languages.length > 1 && (
          <select
            aria-label="Language"
            value={lang ?? ""}
            onChange={(e) => setLang(e.target.value)}
            className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
          >
            {doc.site.languages.map((l) => (
              <option key={l} value={l}>
                {meta.languages[l] ?? l}
              </option>
            ))}
          </select>
        )}
        <div className="inline-flex overflow-hidden rounded-md border border-slate-300 text-sm" role="group" aria-label="Preview size">
          {(["desktop", "mobile"] as const).map((d) => (
            <button
              key={d}
              onClick={() => setDevice(d)}
              aria-pressed={device === d}
              className={`px-3 py-1 capitalize ${device === d ? "bg-slate-900 text-white" : "bg-white text-slate-600 hover:bg-slate-50"}`}
            >
              {d}
            </button>
          ))}
        </div>
        <Button variant="ghost" onClick={() => downloadExport(project.id, project.slug)}>
          Export ZIP
        </Button>
      </div>
    </header>
  );
}
