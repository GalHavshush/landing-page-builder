import { Monitor, Moon, Sun } from "lucide-react";
import { setThemePref, useThemePref, type ThemePref } from "@/theme";
import { t } from "@/i18n";

const OPTIONS: { value: ThemePref; label: string; Icon: typeof Sun }[] = [
  { value: "light", label: "Light", Icon: Sun },
  { value: "system", label: "System", Icon: Monitor },
  { value: "dark", label: "Dark", Icon: Moon },
];

/** Three-way switch: light, follow system, dark. */
export function ThemeToggle() {
  const pref = useThemePref();
  return (
    <div role="group" aria-label={t("Color theme")} className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200">
      {OPTIONS.map(({ value, label, Icon }) => (
        <button key={value} type="button" aria-label={t("{name} theme", { name: t(label) })} title={t("{name} theme", { name: t(label) })} aria-pressed={pref === value} onClick={() => setThemePref(value)}
          className={`grid h-6 w-7 place-items-center rounded-[5px] transition ${pref === value ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-500 hover:text-ink-900"}`}>
          <Icon size={13} strokeWidth={1.7} />
        </button>
      ))}
    </div>
  );
}
