import { useState } from "react";
import type { EditorMeta } from "@/api/types";
import { designChecks } from "./designChecks";
import { BrandPanel } from "./settings/BrandPanel";
import { ChecksPanel } from "./settings/ChecksPanel";
import { LanguagePanel } from "./settings/LanguagePanel";
import { PagePanel } from "./settings/PagePanel";
import { SitePanel } from "./settings/SitePanel";
import { ThemePanel } from "./settings/ThemePanel";
import { useCanEditStructure, useEditor } from "./store";
import { t } from "@/i18n";

const TABS = ["page", "site", "brand", "theme", "languages", "checks"] as const;
const TAB_LABEL: Record<(typeof TABS)[number], string> = { page: "Page", site: "Site", brand: "Brand", theme: "Theme", languages: "Languages", checks: "Checks" };

/** Shown when no section is selected: page, site-wide, theme and language settings. */
export function SettingsPanel({ meta }: { meta: EditorMeta }) {
  const [tab, setTab] = useState<(typeof TABS)[number]>("page");
  const canEdit = useCanEditStructure();
  const issueCount = useEditor((st) => (st.doc ? designChecks(st.doc).length : 0));
  const tabs = canEdit ? TABS : (["page", "site"] as const); // clients: search texts and business info only
  return (
    <aside className="flex min-h-0 flex-col border-s border-ink-200 bg-white">
      <div className="border-b border-ink-200 px-4 pt-3.5">
        <h2 className="text-[13px] font-semibold tracking-tight">{t("Site settings")}</h2>
        <div role="tablist" className="mt-2.5 flex flex-wrap gap-x-3.5">
          {tabs.map((k) => (
            <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}
              className={`-mb-px border-b-[1.5px] py-2 text-[13px] font-medium transition ${tab === k ? "border-ink-900 text-ink-900" : "border-transparent text-ink-500 hover:text-ink-800"}`}>
              {t(TAB_LABEL[k])}{k === "checks" && issueCount > 0 && <span className="ms-1.5 rounded-full bg-amber-100 px-1.5 text-[10.5px] text-amber-800">{issueCount}</span>}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {tab === "page" && <PagePanel />}
        {tab === "site" && <SitePanel />}
        {tab === "brand" && <BrandPanel />}
        {tab === "theme" && <ThemePanel meta={meta} />}
        {tab === "checks" && <ChecksPanel />}
        {tab === "languages" && <LanguagePanel meta={meta} />}
      </div>
    </aside>
  );
}
