import { Monitor, Moon, Sun } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { IconSettings } from "@/components/icons";
import { setUiLang, t, UI_LANGUAGES, useUiLang } from "@/i18n";
import { setThemePref, useThemePref, type ThemePref } from "@/theme";

const THEMES: { value: ThemePref; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "system", label: "Match my device" },
  { value: "dark", label: "Dark" },
];

type Size = "md" | "sm";

function Choice({ checked, onSelect, children, name, size }: { checked: boolean; onSelect: () => void; children: React.ReactNode; name: string; size: Size }) {
  return (
    <label className={`cursor-pointer rounded-lg border font-medium transition ${size === "sm" ? "px-3 py-1.5 text-[12px]" : "px-4 py-2.5 text-[13px]"} ${checked ? "border-ink-900 shadow-[0_0_0_1px_var(--color-ink-900)]" : "border-ink-200 hover:border-ink-400"}`}>
      <input type="radio" name={name} checked={checked} onChange={onSelect} className="sr-only" />
      {children}
    </label>
  );
}

/** The editor's language. `onPicked` lets signed-in screens save the choice to the account. */
export function LanguageChoice({ labelledBy, onPicked, size = "md" }: { labelledBy: string; onPicked?: (l: (typeof UI_LANGUAGES)[number]["value"]) => void; size?: Size }) {
  const lang = useUiLang();
  return (
    <div role="radiogroup" aria-labelledby={labelledBy} className="flex flex-wrap gap-2">
      {UI_LANGUAGES.map((l) => (
        <Choice key={l.value} name="ui-language" size={size} checked={lang === l.value} onSelect={() => { setUiLang(l.value); onPicked?.(l.value); }}>
          {l.label}
        </Choice>
      ))}
    </div>
  );
}

/** Light, dark or follow the device. */
export function ThemeChoice({ labelledBy, onPicked, size = "md" }: { labelledBy: string; onPicked?: (t: ThemePref) => void; size?: Size }) {
  const theme = useThemePref();
  return (
    <div role="radiogroup" aria-labelledby={labelledBy} className="flex flex-wrap gap-2">
      {THEMES.map((o) => (
        <Choice key={o.value} name="ui-theme" size={size} checked={theme === o.value} onSelect={() => { setThemePref(o.value); onPicked?.(o.value); }}>
          {t(o.label)}
        </Choice>
      ))}
    </div>
  );
}

const THEME_ICONS = { light: Sun, system: Monitor, dark: Moon } as const;

/** Language and theme behind one gear button (for screens with no room for full settings). */
export function PreferencesMenu() {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const theme = useThemePref();
  const langId = useId();
  const themeId = useId();

  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => !root.current?.contains(e.target as Node) && setOpen(false);
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("mousedown", away);
      document.removeEventListener("keydown", esc);
    };
  }, [open]);

  return (
    <div ref={root} className="relative">
      <button type="button" aria-label={t("Settings")} title={t("Settings")} aria-haspopup="true" aria-expanded={open} onClick={() => setOpen(!open)}
        className={`grid h-8 w-8 place-items-center rounded-md border border-ink-200 text-ink-600 transition hover:border-ink-400 hover:text-ink-900 ${open ? "bg-ink-100 text-ink-900" : ""}`}>
        <IconSettings size={15} />
      </button>
      {open && (
        <div className="absolute end-0 top-10 z-10 w-56 space-y-4 rounded-xl border border-ink-200 bg-white p-3 shadow-pop">
          <div>
            <div id={langId} className="mb-1.5 text-[12px] font-medium text-ink-500">{t("Editor language")}</div>
            <LanguageChoice labelledBy={langId} size="sm" />
          </div>
          <div>
            <div id={themeId} className="mb-1.5 text-[12px] font-medium text-ink-500">{t("Theme")}</div>
            <div role="radiogroup" aria-labelledby={themeId} className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200">
              {THEMES.map((o) => {
                const Icon = THEME_ICONS[o.value];
                return (
                  <button key={o.value} type="button" role="radio" aria-checked={theme === o.value} aria-label={t(o.label)} title={t(o.label)} onClick={() => setThemePref(o.value)}
                    className={`grid h-7 flex-1 place-items-center rounded-[5px] transition ${theme === o.value ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-500 hover:text-ink-900"}`}>
                    <Icon size={14} strokeWidth={1.7} />
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
