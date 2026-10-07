import { useRef, useState } from "react";
import { useCreateExport, useExports, type SiteExport } from "@/api/hooks";
import { IconDownload } from "@/components/icons";
import { IconClose } from "@/components/icons";
import { Button, linkButton } from "@/components/ui";
import { saver } from "./saving";
import { t } from "@/i18n";

const kb = (n: number) => (n > 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);
const when = (iso: string) => new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
const href = (projectId: number, id: number) => `/api/projects/${projectId}/exports/${id}/download`;

function Issues({ issues }: { issues: SiteExport["issues"] }) {
  const warnings = issues.filter((i) => i.level === "warning");
  const info = issues.filter((i) => i.level === "info");
  if (!issues.length) return <p className="text-sm text-emerald-700">{t("No problems found.")}</p>;
  return (
    <div className="space-y-2 text-sm">
      {warnings.length > 0 && (
        <div>
          <div className="font-medium text-amber-800">{t("Worth fixing ({n})", { n: warnings.length })}</div>
          <ul className="mt-1 list-disc space-y-0.5 ps-5 text-ink-700">
            {warnings.map((i, k) => <li key={k}>{t(i.message)}{i.where && <span className="text-ink-500"> · {i.where}</span>}</li>)}
          </ul>
        </div>
      )}
      {info.length > 0 && (
        <div>
          <div className="font-medium text-ink-600">{t("Suggestions ({n})", { n: info.length })}</div>
          <ul className="mt-1 list-disc space-y-0.5 ps-5 text-ink-500">
            {info.map((i, k) => <li key={k}>{i.message}{i.where && <span className="text-ink-500"> · {i.where}</span>}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

/** Builds the saved site into a ZIP, shows what the builder noticed, and keeps a history. */
export function ExportDialog({ projectId }: { projectId: number }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const history = useExports(projectId, open);
  const create = useCreateExport(projectId);
  const [latest, setLatest] = useState<SiteExport | null>(null);

  const build = async () => {
    await saver.current?.flush(); // export what the user sees, not the last autosave
    create.mutate(undefined, { onSuccess: setLatest });
  };

  return (
    <>
      <Button onClick={() => { setLatest(null); setOpen(true); dialog.current?.showModal(); }}><IconDownload size={14} />{t("Export")}</Button>
      <dialog ref={dialog} className="m-auto w-[min(36rem,94vw)] rounded-2xl bg-white p-0"
        onClose={() => setOpen(false)} onClick={(e) => e.target === dialog.current && dialog.current?.close()}>
        <div className="space-y-5 p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-semibold tracking-tight">{t("Export your site")}</h2>
            <button aria-label={t("Close")} className="grid h-7 w-7 place-items-center rounded-md text-ink-500 hover:bg-ink-100 hover:text-ink-900" onClick={() => dialog.current?.close()}><IconClose size={15} /></button>
          </div>
          <p className="text-sm text-ink-600">
            {t("You get a ZIP with a complete, ready-to-publish website. Upload its contents to any static host (Cloudflare Pages, Netlify, GitHub Pages, your own server). The ZIP also contains your site's source, so you can always take it elsewhere.")}
          </p>

          {!latest ? (
            <Button onClick={build} disabled={create.isPending}>{create.isPending ? t("Building…") : t("Create new export")}</Button>
          ) : (
            <section className="space-y-3 rounded-lg border border-emerald-200 bg-emerald-50/50 p-3">
              <div className="text-sm font-medium">{t("Export ready · {files} files · {size}", { files: latest.file_count, size: kb(latest.size_bytes) })}</div>
              <Issues issues={latest.issues} />
              <div className="flex flex-wrap items-center gap-2">
                <a href={href(projectId, latest.id)} download className={linkButton}>
                  {t("Download ZIP")}
                </a>
                <Button variant="ghost" onClick={build} disabled={create.isPending}>{create.isPending ? t("Building…") : t("Export again")}</Button>
              </div>
            </section>
          )}
          {create.error && <p role="alert" className="text-sm text-red-600">{create.error.message}</p>}

          {!!history.data?.length && (
            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-500">{t("Previous exports")}</h3>
              <ul className="divide-y divide-ink-100 rounded-md border border-ink-200 text-sm">
                {history.data.map((e) => (
                  <li key={e.id} className="flex items-center justify-between gap-3 px-3 py-2">
                    <span>{when(e.created_at)}<span className="ms-2 text-xs text-ink-500">{t("by {name} · v{rev} · {size}", { name: e.created_by, rev: e.doc_revision, size: kb(e.size_bytes) })}</span></span>
                    <a className="text-ink-700 underline decoration-ink-300 underline-offset-2 hover:decoration-ink-900" href={href(projectId, e.id)} download>{t("Download")}</a>
                  </li>
                ))}
              </ul>
              <p className="mt-1 text-xs text-ink-500">{t("The last 10 exports are kept.")}</p>
            </section>
          )}
        </div>
      </dialog>
    </>
  );
}
