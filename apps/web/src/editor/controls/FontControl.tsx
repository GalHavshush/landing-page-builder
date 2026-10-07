import { useEffect, useId } from "react";
import type { FontOption } from "@/api/types";
import { FieldShell } from "./basic";
import { t } from "@/i18n";

const loaded = new Set<string>();

/** Loads a bundled font into the editor so the sample line can be drawn in it. */
function ensureFont(option: FontOption) {
  if (!option.file || loaded.has(option.key)) return;
  loaded.add(option.key);
  const face = new FontFace(option.label, `url(/api/fonts/${option.file})`, { weight: "100 900" });
  face.load().then((f) => document.fonts.add(f)).catch(() => loaded.delete(option.key));
}

const GROUPS: { kind: FontOption["kind"]; title: string }[] = [
  { kind: "sans", title: "Sans-serif" },
  { kind: "serif", title: "Serif" },
  { kind: "system", title: "System (no download, instant)" },
];

/** Font picker: grouped list plus a live sample set in the chosen face. */
export function FontControl({
  label, value, options, onChange, siteHasScripts,
}: {
  label: string;
  value: string;
  options: FontOption[];
  onChange: (key: string) => void;
  siteHasScripts: string[]; // scripts the site's languages need, e.g. ["hebrew"]
}) {
  const id = useId();
  const current = options.find((o) => o.key === value);
  useEffect(() => { if (current) ensureFont(current); }, [current]);
  const lacking = current && current.kind !== "system" ? siteHasScripts.filter((s) => !current.scripts.includes(s)) : [];

  return (
    <FieldShell label={label} htmlFor={id}>
      <select id={id} className="field-input" value={value} onChange={(e) => onChange(e.target.value)}>
        {GROUPS.map((g) => (
          <optgroup key={g.kind} label={t(g.title)}>
            {options.filter((o) => o.kind === g.kind).map((o) => (
              <option key={o.key} value={o.key}>{o.label}</option>
            ))}
          </optgroup>
        ))}
      </select>
      {current && (
        <p className="mt-2 truncate text-[17px] leading-tight text-ink-800" style={{ fontFamily: current.kind === "system" ? undefined : `"${current.label}", system-ui` }}>
          {t("Fresh bread, every morning")}
        </p>
      )}
      {lacking.length > 0 && (
        <p className="mt-1.5 text-[12px] leading-snug text-accent-700">
          {t("{font} has no {scripts} letters. Visitors will see a fallback font for that language.", { font: current!.label, scripts: lacking.map((s) => t(s)).join(" / ") })}
        </p>
      )}
    </FieldShell>
  );
}
