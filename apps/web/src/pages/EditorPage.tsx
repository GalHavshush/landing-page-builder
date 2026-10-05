import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useDocument, useEditorMeta, useProject } from "@/api/hooks";
import { PostWorkspace } from "@/editor/blog/PostWorkspace";
import { LeftRail } from "@/editor/LeftRail";
import { Preview, usePreviewHtml } from "@/editor/Preview";
import { PropertiesPanel } from "@/editor/PropertiesPanel";
import { useAutosave, useShortcuts } from "@/editor/saving";
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
    if (docQuery.data && project.data)
      load(projectId, docQuery.data.doc, docQuery.data.revision, project.data.role as "owner" | "designer" | "editor");
  }, [docQuery.data, project.data, projectId, load]);

  if (project.error || docQuery.error)
    return <div className="p-8 text-red-600">Could not open this site.</div>;
  if (!project.data || !meta.data || loadedFor !== projectId)
    return <div className="p-8 text-ink-500">Loading editor…</div>;

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
  const view = useEditor((s) => s.view);
  const saveStatus = useEditor((s) => s.saveStatus);
  const saveError = useEditor((s) => s.saveError);
  useAutosave(projectId);
  useShortcuts();

  return (
    <div className="grid h-screen grid-rows-[2.75rem_1fr]">
      <TopBar project={project} meta={meta} />
      <div className="grid min-h-0 grid-cols-[256px_1fr_312px]">
        <LeftRail meta={meta} />
        {view === "blog" ? (
          <PostWorkspace />
        ) : (
        <>
        <main className="relative min-h-0">
          <Preview html={html} />
          {(saveStatus === "conflict" || saveStatus === "invalid") && (
            <div role="alert" className="absolute inset-x-4 bottom-4 flex items-center justify-between gap-3 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">
              <span>{saveError}</span>
              {saveStatus === "conflict" && (
                <button className="rounded bg-white/20 px-2 py-1 hover:bg-white/30" onClick={() => window.location.reload()}>
                  Reload latest
                </button>
              )}
            </div>
          )}
          {error && (
            <div role="alert" className="absolute inset-x-4 top-4 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">
              Preview failed: {error}
            </div>
          )}
        </main>
        <PropertiesPanel meta={meta} />
        </>
        )}
      </div>
    </div>
  );
}
