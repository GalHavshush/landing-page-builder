import type { EditorMeta } from "@/api/types";
import { Button } from "@/components/ui";
import { useState } from "react";
import { addLanguage, removeLanguage } from "../commands";
import { useEditor } from "../store";

export function LanguagePanel({ meta }: { meta: EditorMeta }) {
  const site = useEditor((s) => s.doc)!.site;
  const apply = useEditor((s) => s.apply);
  const setLang = useEditor((s) => s.setLang);
  const lang = useEditor((s) => s.lang);
  const available = Object.keys(meta.languages).filter((c) => !site.languages.includes(c));
  const [choice, setChoice] = useState("");
  const name = (c: string) => meta.languages[c] ?? c;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-600">
        Every language shares the same pages and design. Switch language in the top bar to translate text; anything not translated shows the default language.
      </p>
      <ul className="space-y-1.5">
        {site.languages.map((c) => (
          <li key={c} className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-sm">
            <span>
              {name(c)} <span className="text-slate-400">({c})</span>
              {c === site.default_language && <span className="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">default</span>}
              {meta.rtl_languages.includes(c.split("-")[0]) && <span className="ml-2 text-xs text-slate-400">right-to-left</span>}
            </span>
            {c !== site.default_language && (
              <button className="text-xs text-slate-500 hover:text-red-600"
                onClick={() => {
                  if (!window.confirm(`Remove ${name(c)} and all its translations?`)) return;
                  if (lang === c) setLang(site.default_language);
                  apply(removeLanguage(c));
                }}>
                Remove
              </button>
            )}
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        <select aria-label="Language to add" value={choice} onChange={(e) => setChoice(e.target.value)}
          className="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm">
          <option value="">Add a language…</option>
          {available.map((c) => <option key={c} value={c}>{name(c)}</option>)}
        </select>
        <Button type="button" disabled={!choice} onClick={() => { apply(addLanguage(choice)); setChoice(""); }}>Add</Button>
      </div>
    </div>
  );
}
