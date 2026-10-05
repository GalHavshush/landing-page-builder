import { Link, useNavigate } from "react-router-dom";
import { useSavePreferences } from "@/api/hooks";
import { IconBack } from "@/components/icons";
import { LanguageChoice, ThemeChoice } from "@/components/Preferences";
import { t } from "@/i18n";

/** Account-wide settings: the editor's own language and theme. They say nothing about any website's language. */
export default function SettingsPage() {
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
          <div className="mt-3"><LanguageChoice labelledBy="ui-lang" onPicked={(l) => save.mutate({ ui_language: l })} /></div>
        </section>
        <section aria-labelledby="ui-theme">
          <h2 id="ui-theme" className="text-[15px] font-semibold tracking-tight">{t("Theme")}</h2>
          <p className="mt-1 text-[13px] text-ink-500">{t("Light or dark editor. Your websites keep their own colours.")}</p>
          <div className="mt-3"><ThemeChoice labelledBy="ui-theme" onPicked={(v) => save.mutate({ ui_theme: v })} /></div>
        </section>
        {save.isError && <p role="alert" className="text-[13px] text-red-600">{t("Couldn't save your settings. They will apply on this device only.")}</p>}
        <Link to="/" className="inline-block text-[13px] text-ink-600 underline decoration-ink-300 underline-offset-4 hover:text-ink-900">{t("All sites")}</Link>
      </main>
    </div>
  );
}
