import { designChecks } from "../designChecks";
import { useEditor } from "../store";
import { t } from "@/i18n";

/** Plain-language suggestions for the whole site. Clicking one jumps to the section it is about. */
export function ChecksPanel() {
  const doc = useEditor((s) => s.doc)!;
  const selectPage = useEditor((s) => s.selectPage);
  const selectSection = useEditor((s) => s.selectSection);
  const checks = designChecks(doc);
  const title = (id: string) => doc.pages.find((p) => p.id === id)?.title ?? "";

  if (checks.length === 0) return <p className="text-[13px] text-ink-500">{t("Nothing to fix. The layout looks balanced.")}</p>;
  return (
    <ul className="space-y-2">
      {checks.map((c, i) => (
        <li key={i}>
          <button type="button" className="w-full rounded-md border border-ink-200 p-2.5 text-start text-[13px] transition hover:border-ink-400"
            onClick={() => { selectPage(c.pageId); selectSection(c.sectionId); }}>
            <span className={`me-1.5 inline-block rounded px-1.5 py-px text-[10.5px] font-semibold uppercase tracking-wide ${c.level === "warn" ? "bg-amber-100 text-amber-800" : "bg-ink-100 text-ink-600"}`}>
              {c.level === "warn" ? t("Fix") : t("Tip")}
            </span>
            <span className="text-ink-500">{title(c.pageId)}</span>
            <span className="mt-1 block text-ink-800">{c.message}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
