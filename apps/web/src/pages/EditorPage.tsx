import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useDocument, useEditorMeta, useProject } from "@/api/hooks";
import { PostWorkspace } from "@/editor/blog/PostWorkspace";
import { LeftRail } from "@/editor/LeftRail";
import { Preview, usePreviewHtml } from "@/editor/Preview";
import { PropertiesPanel } from "@/editor/PropertiesPanel";
import { useAutosave, useShortcuts } from "@/editor/saving";
import { useEditor } from "@/editor/store";
import { TopBar } from "@/editor/TopBar";
import { t } from "@/i18n";

export default function EditorPage() {
  const projectId = Number(useParams().projectId);
  const project = useProject(projectId);
  const docQuery = useDocument(projectId);
  const siteLang = useEditor((s) => s.doc?.site.default_language);
  const meta = useEditorMeta(siteLang);
  const load = useEditor((s) => s.load);
  const loadedFor = useEditor((s) => s.projectId);

  useEffect(() => {
    if (docQuery.data && project.data)
      load(projectId, docQuery.data.doc, docQuery.data.revision, project.data.role as "owner" | "designer" | "editor");
  }, [docQuery.data, project.data, projectId, load]);

  if (project.error || docQuery.error)
    return <div className="p-8 text-red-600">{t("Could not open this site.")}</div>;
  if (!project.data || !meta.data || loadedFor !== projectId)
    return <div className="p-8 text-ink-500">{t("Loading editor…")}</div>;

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

  // Below 1024px the three panels become one at a time, switched from a bar at the bottom.
  const [pane, setPane] = useState<"pages" | "preview" | "settings">("preview");
  const selectedId = useEditor((s) => s.selectedId);
  useEffect(() => {
    if (selectedId && window.matchMedia("(max-width: 1023px)").matches) setPane("settings");
  }, [selectedId]);
  const show = (p: typeof pane) => (pane === p ? "contents" : "hidden lg:contents");

  return (
    <div className="grid h-dvh grid-rows-[2.75rem_1fr_auto] lg:grid-rows-[2.75rem_1fr]">
      <TopBar project={project} meta={meta} />
      <div className="grid min-h-0 grid-cols-1 lg:grid-cols-[256px_1fr_344px]">
        <div className={show("pages")}><LeftRail meta={meta} /></div>
        {view === "blog" ? (
          <div className={pane === "preview" ? "contents" : "hidden lg:contents"}><PostWorkspace /></div>
        ) : (
        <>
        <main className={`relative min-h-0 ${pane === "preview" ? "" : "hidden lg:block"}`}>
          <Preview html={html} />
          {(saveStatus === "conflict" || saveStatus === "invalid") && (
            <div role="alert" className="absolute inset-x-4 bottom-4 flex items-center justify-between gap-3 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">
              <span>{saveError}</span>
              {saveStatus === "conflict" && (
                <button className="rounded bg-white/20 px-2 py-1 hover:bg-white/30" onClick={() => window.location.reload()}>
                  {t("Reload latest")}
                </button>
              )}
            </div>
          )}
          {error && (
            <div role="alert" className="absolute inset-x-4 top-4 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">
              {t("Preview failed: {error}", { error: t(error) })}
            </div>
          )}
        </main>
        <div className={show("settings")}><PropertiesPanel meta={meta} /></div>
        </>
        )}
      </div>
      <nav aria-label={t("Editor sections")} className="grid grid-cols-3 border-t border-ink-200 bg-white lg:hidden">
        {([["pages", "Pages"], ["preview", "Preview"], ["settings", "Settings"]] as const).map(([k, l]) => (
          <button key={k} aria-pressed={pane === k} onClick={() => setPane(k)}
            className={`py-2.5 text-[13px] font-medium ${pane === k ? "text-ink-900 shadow-[inset_0_2px_0_var(--color-ink-900)]" : "text-ink-500"}`}>{t(l)}</button>
        ))}
      </nav>
    </div>
  );
}
