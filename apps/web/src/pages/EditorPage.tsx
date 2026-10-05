import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useDocument, useEditorMeta, useProject } from "@/api/hooks";
import { LeftRail } from "@/editor/LeftRail";
import { Preview, usePreviewHtml } from "@/editor/Preview";
import { RightPanel } from "@/editor/RightPanel";
import { useEditor } from "@/editor/store";
import { TopBar } from "@/editor/TopBar";

export default function EditorPage() {
  const projectId = Number(useParams().projectId);
  const project = useProject(projectId);
  const docQuery = useDocument(projectId);
  const meta = useEditorMeta();
  const load = useEditor((s) => s.load);
  const loadedFor = useEditor((s) => s.projectId);

  useEffect(() => {
    if (docQuery.data) load(projectId, docQuery.data.doc, docQuery.data.revision);
  }, [docQuery.data, projectId, load]);

  if (project.error || docQuery.error)
    return <div className="p-8 text-red-600">Could not open this site.</div>;
  if (!project.data || !meta.data || loadedFor !== projectId)
    return <div className="p-8 text-slate-500">Loading editor…</div>;

  return <EditorShell projectId={projectId} project={project.data} meta={meta.data} />;
}

function EditorShell({
  projectId,
  project,
  meta,
}: {
  projectId: number;
  project: NonNullable<ReturnType<typeof useProject>["data"]>;
  meta: NonNullable<ReturnType<typeof useEditorMeta>["data"]>;
}) {
  const doc = useEditor((s) => s.doc)!;
  const pageId = useEditor((s) => s.pageId)!;
  const lang = useEditor((s) => s.lang)!;
  const { html, error } = usePreviewHtml(projectId, doc, pageId, lang);

  return (
    <div className="grid h-screen grid-rows-[3.25rem_1fr]">
      <TopBar project={project} meta={meta} />
      <div className="grid min-h-0 grid-cols-[260px_1fr_320px]">
        <LeftRail meta={meta} />
        <main className="relative min-h-0">
          <Preview html={html} />
          {error && (
            <div role="alert" className="absolute inset-x-4 top-4 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">
              Preview failed: {error}
            </div>
          )}
        </main>
        <RightPanel />
      </div>
    </div>
  );
}
