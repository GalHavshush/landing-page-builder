import { Link, useNavigate } from "react-router-dom";
import { useSavePreferences } from "@/api/hooks";
import { IconBack } from "@/components/icons";
import { t, UI_LANGUAGES, setUiLang, useUiLang } from "@/i18n";
import { setThemePref, useThemePref, type ThemePref } from "@/theme";

const THEMES: { value: ThemePref; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "system", label: "Match my device" },
  { value: "dark", label: "Dark" },
];

function Choice({ checked, onSelect, children, name }: { checked: boolean; onSelect: () => void; children: React.ReactNode; name: string }) {
  return (
    <label className={`cursor-pointer rounded-lg border px-4 py-2.5 text-[13px] font-medium transition ${checked ? "border-ink-900 shadow-[0_0_0_1px_var(--color-ink-900)]" : "border-ink-200 hover:border-ink-400"}`}>
      <input type="radio" name={name} checked={checked} onChange={onSelect} className="sr-only" />
      {children}
    </label>
  );
}

/** Account-wide settings: the editor's own language and theme. They say nothing about any website's language. */
export default function SettingsPage() {
  const lang = useUiLang();
  const theme = useThemePref();
  const save = useSavePreferences();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <header className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex h-12 max-w-3xl items-center gap-3 px-6">
          <button type="button" aria-label={t("Back")} title={t("Back")} onClick={() => navigate(-1)}
            className="grid h-7 w-7 place-items-center rounded-md text-ink-600 hover:bg-ink-100 hover:text-ink-900"><IconBack size={15} /></button>
          <h1 className="text-[13px] font-semibold tracking-tight">{t("Settings")}</h1>
        </div>
      </header>
      <main className="mx-auto max-w-3xl space-y-10 px-6 py-10">
        <section aria-labelledby="ui-lang">
          <h2 id="ui-lang" className="text-[15px] font-semibold tracking-tight">{t("Editor language")}</h2>
          <p className="mt-1 text-[13px] text-ink-500">{t("The language of the editor's menus and buttons. It does not change the language of your websites.")}</p>
          <div role="radiogroup" aria-labelledby="ui-lang" className="mt-3 flex flex-wrap gap-2">
            {UI_LANGUAGES.map((l) => (
              <Choice key={l.value} name="ui-language" checked={lang === l.value} onSelect={() => { setUiLang(l.value); save.mutate({ ui_language: l.value }); }}>
                {l.label}
              </Choice>
            ))}
          </div>
        </section>
        <section aria-labelledby="ui-theme">
          <h2 id="ui-theme" className="text-[15px] font-semibold tracking-tight">{t("Theme")}</h2>
          <p className="mt-1 text-[13px] text-ink-500">{t("Light or dark editor. Your websites keep their own colours.")}</p>
          <div role="radiogroup" aria-labelledby="ui-theme" className="mt-3 flex flex-wrap gap-2">
            {THEMES.map((o) => (
              <Choice key={o.value} name="ui-theme" checked={theme === o.value} onSelect={() => { setThemePref(o.value); save.mutate({ ui_theme: o.value }); }}>
                {t(o.label)}
              </Choice>
            ))}
          </div>
        </section>
        {save.isError && <p role="alert" className="text-[13px] text-red-600">{t("Couldn't save your settings. They will apply on this device only.")}</p>}
        <Link to="/" className="inline-block text-[13px] text-ink-600 underline decoration-ink-300 underline-offset-4 hover:text-ink-900">{t("All sites")}</Link>
      </main>
    </div>
  );
}
