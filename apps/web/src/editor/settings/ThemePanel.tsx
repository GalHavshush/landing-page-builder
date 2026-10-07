import type { EditorMeta, SiteDocument } from "@/api/types";
import { balanceBackgrounds, updateTheme } from "../commands";
import { SegmentedControl, SelectControl } from "../controls/basic";
import { FontControl } from "../controls/FontControl";
import { ColorControl } from "../controls/ColorControl";
import { contrastRatio, isHex, MIN_CONTRAST } from "../contrast";
import { useEditor } from "../store";
import { paletteFromBrand } from "../palette";
import { t } from "@/i18n";

type Palette = SiteDocument["theme"]["palette"];

const LANG_SCRIPT: Record<string, string> = { he: "hebrew", yi: "hebrew", ar: "arabic", fa: "arabic", ur: "arabic" };
/** Scripts (beyond Latin) that the site's languages need, so the picker can warn about fonts lacking them. */
export const scriptsFor = (languages: string[]) =>
  [...new Set(languages.map((l) => LANG_SCRIPT[l.split("-")[0]]).filter(Boolean))];

export const PALETTES: Record<string, Palette> = {
  Ocean: { primary: "#2563EB", accent: "#F59E0B", background: "#FFFFFF", surface: "#F3F4F6", text: "#111827" },
  Warm: { primary: "#B4532A", accent: "#E0A458", background: "#FFFBF5", surface: "#F6EEE3", text: "#2B2118" },
  Forest: { primary: "#2F6F4F", accent: "#D9A441", background: "#FBFCF9", surface: "#EEF3EA", text: "#1B2A22" },
  Rose: { primary: "#BE185D", accent: "#F59E0B", background: "#FFFFFF", surface: "#FDF2F8", text: "#1F2937" },
  Midnight: { primary: "#6366F1", accent: "#22D3EE", background: "#0F172A", surface: "#1E293B", text: "#F1F5F9" },
  Mono: { primary: "#111827", accent: "#9CA3AF", background: "#FFFFFF", surface: "#F5F5F5", text: "#111827" },
};

const LABELS: Record<keyof Palette, string> = {
  primary: "Brand color", accent: "Accent color", background: "Page background", surface: "Panel background", text: "Text color",
};

export function ThemePanel({ meta }: { meta: EditorMeta }) {
  const doc = useEditor((s) => s.doc)!;
  const theme = doc.theme;
  const neededScripts = scriptsFor(doc.site.languages);
  const apply = useEditor((s) => s.apply);
  const setColor = (key: keyof Palette, v: string, typing?: boolean) =>
    apply((d) => { d.theme.palette[key] = v; }, { coalesceKey: typing ? `theme.${key}` : undefined });

  const warnings = (["background", "surface"] as const)
    .filter((bg) => isHex(theme.palette.text) && isHex(theme.palette[bg]) && contrastRatio(theme.palette.text, theme.palette[bg]) < MIN_CONTRAST)
    .map((bg) => t("Text on {on} is hard to read ({ratio}:1, aim for {min}:1).", { on: t(LABELS[bg]).toLowerCase(), ratio: contrastRatio(theme.palette.text, theme.palette[bg]).toFixed(1), min: MIN_CONTRAST }));

  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs font-medium text-ink-600">{t("Look")}</div>
        <p className="text-xs text-ink-500">{t("Switch colours, fonts and style. Your content stays as it is.")}</p>
        <div className="mt-1.5 grid grid-cols-2 gap-2">
          {meta.starter_info.map((st) => (
            <button key={st.id} type="button" aria-pressed={theme.template === st.theme.template}
              onClick={() => apply(updateTheme({ ...st.theme }))}
              className="rounded-md border border-ink-200 p-1.5 text-start text-xs hover:border-ink-400 aria-pressed:border-accent-600">
              <div className="mb-1 flex h-5 overflow-hidden rounded">
                {Object.values(st.theme.palette).map((c, i) => <span key={i} className="flex-1" style={{ background: c }} />)}
              </div>
              {t(st.label)}
            </button>
          ))}
        </div>
      </div>
      <div>
        <div className="text-xs font-medium text-ink-600">{t("Color schemes")}</div>
        <div className="mt-1.5 grid grid-cols-3 gap-2">
          {Object.entries(PALETTES).map(([name, p]) => (
            <button key={name} type="button" onClick={() => apply(updateTheme({ palette: { ...p } }))}
              className="rounded-md border border-ink-200 p-1.5 text-start text-xs hover:border-ink-400">
              <div className="mb-1 flex h-5 overflow-hidden rounded">
                {[p.primary, p.accent, p.background, p.surface, p.text].map((c, i) => (
                  <span key={i} className="flex-1" style={{ background: c }} />
                ))}
              </div>
              {t(name)}
            </button>
          ))}
        </div>
      </div>
      <div className="flex gap-2">
        <button type="button" className="flex-1 rounded-md border border-ink-200 px-2 py-1.5 text-xs hover:border-ink-400"
          onClick={() => apply(updateTheme({ palette: paletteFromBrand(theme.palette.primary, "light") }))}>
          {t("Build light palette from brand color")}
        </button>
        <button type="button" className="flex-1 rounded-md border border-ink-200 px-2 py-1.5 text-xs hover:border-ink-400"
          onClick={() => apply(updateTheme({ palette: paletteFromBrand(theme.palette.primary, "dark") }))}>
          {t("Dark version")}
        </button>
      </div>
      {(Object.keys(LABELS) as (keyof Palette)[]).map((key) => (
        <ColorControl key={key} label={LABELS[key]} value={theme.palette[key]} onChange={(v, t) => setColor(key, v, t)} />
      ))}
      {warnings.map((w) => (
        <p key={w} role="alert" className="rounded bg-amber-50 px-2 py-1.5 text-xs text-amber-800">{w}</p>
      ))}
      <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-ink-500">{t("Style")}</h3>
      {(["heading", "body"] as const).map((role) => (
        <FontControl key={role} label={role === "heading" ? "Heading font" : "Body font"} value={theme.fonts[role]}
          options={meta.fonts} siteHasScripts={neededScripts}
          onChange={(v) => apply((d) => { d.theme.fonts[role] = v as typeof theme.fonts.heading; })} />
      ))}
      <SelectControl label="Corner roundness" value={theme.radius} options={meta.radii.map((r) => ({ value: r, label: r }))}
        onChange={(v) => apply(updateTheme({ radius: v as typeof theme.radius }))} />
      <SegmentedControl label="Buttons" value={theme.button_style} options={["solid", "outline", "soft"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ button_style: v as typeof theme.button_style }))} />
      <SegmentedControl label="Spacing" value={theme.spacing} options={["compact", "normal", "spacious"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ spacing: v as typeof theme.spacing }))} />
      <SegmentedControl label="Cards" value={theme.card_style} options={["outlined", "flat", "elevated"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ card_style: v as typeof theme.card_style }))} />
      <SegmentedControl label="Photos" value={theme.image_style} options={["rounded", "square", "soft"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ image_style: v as typeof theme.image_style }))} />
      <SegmentedControl label="Animation" value={theme.motion} options={["none", "subtle", "lively"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ motion: v as typeof theme.motion }))} />
      <SegmentedControl label="Headings" value={theme.heading_style} options={["tight", "caps", "light"].map((v) => ({ value: v, label: v }))}
        onChange={(v) => apply(updateTheme({ heading_style: v as typeof theme.heading_style }))} />
      <button type="button" className="w-full rounded-md border border-ink-200 px-2 py-1.5 text-xs hover:border-ink-400"
        onClick={() => apply(balanceBackgrounds())}>
        {t("Tidy section backgrounds (alternate plain and tinted)")}
      </button>
    </div>
  );
}
