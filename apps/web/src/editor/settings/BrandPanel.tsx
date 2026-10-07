import type { SiteDocument } from "@/api/types";
import { setSiteTranslation } from "../commands";
import { SegmentedControl, TextControl, ToggleControl } from "../controls/basic";
import { ImageControl } from "../controls/ImageControl";
import { LinkControl, type LinkValue } from "../controls/LinkControl";
import { useEditor } from "../store";
import { t } from "@/i18n";

type Site = SiteDocument["site"];
const opts = <T extends string>(...values: T[]) => values.map((value) => ({ value, label: value }));

function Group({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3 border-b border-ink-200 pb-5 last:border-0">
      <div>
        <h3 className="eyebrow-label">{t(title)}</h3>
        {hint && <p className="mt-1 text-[12px] leading-snug text-ink-500">{t(hint)}</p>}
      </div>
      {children}
    </section>
  );
}

/** Logo, header, announcement bar and footer: the frame around every page. */
export function BrandPanel() {
  const doc = useEditor((s) => s.doc)!;
  const lang = useEditor((s) => s.lang)!;
  const apply = useEditor((s) => s.apply);
  const site = doc.site;
  const translating = lang !== site.default_language;
  const tr = site.i18n[lang];
  const pages = doc.pages.map((p) => ({ id: p.id, title: p.title }));
  const set = (fn: (s: Site) => void, key?: string) => apply((d) => fn(d.site), { coalesceKey: key });

  if (translating) {
    return (
      <div className="space-y-4">
        <p className="text-[12px] text-ink-600">{t("Translating the button and banner text. Layout and links are shared.")}</p>
        {site.header.cta && (
          <TextControl label="Header button label" value={tr?.cta_label ?? ""} placeholder={site.header.cta.label}
            onChange={(v, t) => apply(setSiteTranslation(lang, "cta_label", v), { coalesceKey: t ? `site.cta.${lang}` : undefined })} />
        )}
        {site.announcement.enabled && (
          <TextControl label="Announcement text" value={tr?.announcement_text ?? ""} placeholder={site.announcement.text}
            onChange={(v, t) => apply(setSiteTranslation(lang, "announcement_text", v), { coalesceKey: t ? `site.announce.${lang}` : undefined })} />
        )}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <Group title="Logo" hint="Shown instead of the site name, and used as the browser tab icon.">
        <ImageControl label="Logo image" hideAlt={false} value={site.logo} onChange={(v) => set((s) => { s.logo = v; }, v ? "site.logo.alt" : undefined)} />
        {site.logo && <SegmentedControl label="Logo size" value={site.logo_size} options={opts("small", "medium", "large")} onChange={(v) => set((s) => { s.logo_size = v as Site["logo_size"]; })} />}
        {site.logo && <p className="text-[12px] leading-snug text-ink-500">{t("The description above is read out as your business name. Over a dark cover photo the logo is shown in white until the page scrolls.")}</p>}
      </Group>

      <Group title="Header">
        <SegmentedControl label="Layout" value={site.header.style} options={opts("classic", "centered", "split")} onChange={(v) => set((s) => { s.header.style = v as Site["header"]["style"]; })} />
        <ToggleControl label="Stay at the top while scrolling" value={site.header.sticky} onChange={(v) => set((s) => { s.header.sticky = v; })} />
        <ToggleControl label="Transparent over a cover hero" value={site.header.transparent} onChange={(v) => set((s) => { s.header.transparent = v; })} />
        <ToggleControl label="Show a button" value={Boolean(site.header.cta)}
          onChange={(v) => set((s) => { s.header.cta = v ? { label: "Book now", href: { page: pages[0].id, url: null, asset: null }, style: "primary" } : null; })} />
        {site.header.cta && (
          <>
            <TextControl label="Button label" value={site.header.cta.label} onChange={(v, t) => set((s) => { if (s.header.cta) s.header.cta.label = v; }, t ? "site.cta.label" : undefined)} />
            <LinkControl label="Button goes to" value={site.header.cta.href as LinkValue} pages={pages}
              onChange={(v) => set((s) => { if (s.header.cta && v) s.header.cta.href = { page: null, url: null, asset: null, ...v }; })} />
          </>
        )}
      </Group>

      <Group title="Announcement bar" hint="A slim banner above the header, for news, offers or opening changes.">
        <ToggleControl label="Show the bar" value={site.announcement.enabled} onChange={(v) => set((s) => { s.announcement.enabled = v; })} />
        {site.announcement.enabled && (
          <>
            <TextControl label="Text" value={site.announcement.text} onChange={(v, t) => set((s) => { s.announcement.text = v; }, t ? "site.announce.text" : undefined)} />
            <LinkControl label="Link (optional)" optional value={(site.announcement.link as LinkValue | null) ?? null} pages={pages}
              onChange={(v) => set((s) => { s.announcement.link = v ? { page: null, url: null, asset: null, ...v } : null; })} />
          </>
        )}
      </Group>

      <Group title="Footer">
        <SegmentedControl label="Layout" value={site.footer.style} options={opts("columns", "centered", "minimal")} onChange={(v) => set((s) => { s.footer.style = v as Site["footer"]["style"]; })} />
      </Group>
    </div>
  );
}
