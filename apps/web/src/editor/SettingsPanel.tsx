import { useState } from "react";
import type { EditorMeta } from "@/api/types";
import { LanguagePanel } from "./settings/LanguagePanel";
import { PagePanel } from "./settings/PagePanel";
import { SitePanel } from "./settings/SitePanel";
import { ThemePanel } from "./settings/ThemePanel";
import { useCanEditStructure } from "./store";

const TABS = ["page", "site", "theme", "languages"] as const;

/** Shown when no section is selected: page, site-wide, theme and language settings. */
export function SettingsPanel({ meta }: { meta: EditorMeta }) {
  const [tab, setTab] = useState<(typeof TABS)[number]>("page");
  const canEdit = useCanEditStructure();
  const tabs = canEdit ? TABS : (["page", "site"] as const); // clients: search texts and business info only
  return (
    <aside className="flex min-h-0 flex-col border-l border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-4 pt-3">
        <h2 className="text-sm font-semibold">Settings</h2>
        <div role="tablist" className="mt-2 flex gap-3">
          {tabs.map((t) => (
            <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
              className={`-mb-px border-b-2 pb-2 text-sm capitalize ${tab === t ? "border-indigo-600 font-medium text-indigo-700" : "border-transparent text-slate-500 hover:text-slate-800"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {tab === "page" && <PagePanel />}
        {tab === "site" && <SitePanel />}
        {tab === "theme" && <ThemePanel meta={meta} />}
        {tab === "languages" && <LanguagePanel meta={meta} />}
      </div>
    </aside>
  );
}
