import { useEffect, useId, useState } from "react";
import type { SiteDocument } from "@/api/types";
import { setNav, setSiteTranslation, updateSite } from "../commands";
import { FieldShell, SelectControl, TextAreaControl, TextControl, ToggleControl } from "../controls/basic";
import { Repeater } from "../controls/Repeater";
import { useCanEditStructure, useEditor } from "../store";

type Site = SiteDocument["site"];
type Hours = Site["business"]["hours"][number];
type SiteTField = "name" | "tagline" | "description" | "address" | "footer_text";

function BaseUrl({ value, onChange }: { value: string; onChange: (v: string, typing?: boolean) => void }) {
  const id = useId();
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  const bad = draft !== "" && !/^https?:\/\//.test(draft);
  return (
    <FieldShell label="Website address" htmlFor={id} hint="The final address, e.g. https://example.com. Needed for sitemap, social previews and search engines.">
      <input id={id} value={draft} placeholder="https://example.com" aria-invalid={bad} spellCheck={false}
        onChange={(e) => { setDraft(e.target.value); if (e.target.value === "" || /^https?:\/\//.test(e.target.value)) onChange(e.target.value, true); }}
        className={`mt-1 block w-full rounded-md border px-2.5 py-1.5 text-sm ${bad ? "border-red-400" : "border-ink-300"}`} />
      {bad && <p className="mt-1 text-xs text-red-600">Must start with https://</p>}
    </FieldShell>
  );
}

export function SitePanel() {
  const doc = useEditor((s) => s.doc)!;
  const lang = useEditor((s) => s.lang)!;
  const apply = useEditor((s) => s.apply);
  const canEdit = useCanEditStructure();
  const site = doc.site;
  const translating = lang !== site.default_language;
  const tr = site.i18n[lang];

  const base: Record<SiteTField, string> = {
    name: site.name, tagline: site.tagline, description: site.seo.default_description,
    address: site.business.address, footer_text: site.footer.text,
  };
  const value = (f: SiteTField) => (translating ? (tr?.[f] ?? "") : base[f]);
  const write = (f: SiteTField, v: string, typing?: boolean) => {
    const key = typing ? `site.${f}.${lang}` : undefined;
    if (translating) return apply(setSiteTranslation(lang, f, v), { coalesceKey: key });
    apply(
      (d) => {
        if (f === "name") d.site.name = v;
        else if (f === "tagline") d.site.tagline = v;
        else if (f === "description") d.site.seo.default_description = v;
        else if (f === "address") d.site.business.address = v;
        else d.site.footer.text = v;
      },
      { coalesceKey: key },
    );
  };
  const field = (f: SiteTField, label: string, area = false, hint?: string) =>
    area ? (
      <TextAreaControl label={label} hint={hint} value={value(f)} placeholder={translating ? base[f] : undefined} onChange={(v, t) => write(f, v, t)} />
    ) : (
      <TextControl label={label} hint={hint} value={value(f)} placeholder={translating ? base[f] : undefined} onChange={(v, t) => write(f, v, t)} />
    );

  const business = (key: "phone" | "email") => (
    <TextControl label={key === "phone" ? "Phone" : "Email"} value={site.business[key]} onChange={(v) =>
      apply((d) => { d.site.business[key] = v; }, { coalesceKey: `site.${key}` })} />
  );

  return (
    <div className="space-y-4">
      {translating && <p className="text-xs text-accent-600">Translating site text. Phone, email, hours and web address are shared.</p>}
      {canEdit && field("name", "Site name")}
      {field("tagline", "Tagline")}
      {field("description", "Default description", true, "Used in search results when a page has none.")}
      {canEdit && !translating && <BaseUrl value={site.base_url} onChange={(v, t) => apply(updateSite({ base_url: v }), { coalesceKey: t ? "site.base_url" : undefined })} />}

      <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-ink-500">Business info</h3>
      {!translating && business("phone")}
      {!translating && business("email")}
      {field("address", "Address", true)}
      {!translating && (
        <Repeater<Hours>
          label="Opening hours"
          items={site.business.hours as Hours[]}
          onChange={(items, t) => apply((d) => { d.site.business.hours = items; }, { coalesceKey: t ? "site.hours" : undefined })}
          makeBlank={() => ({ label: "Mon-Fri", open: "09:00", close: "17:00", closed: false })}
          addLabel="Add hours"
          renderItem={(h, set) => (
            <>
              <TextControl label="Days" value={h.label} onChange={(v, t) => set({ ...h, label: v }, t)} />
              <ToggleControl label="Closed" value={h.closed} onChange={(v) => set({ ...h, closed: v })} />
              {!h.closed && (
                <div className="grid grid-cols-2 gap-2">
                  <TextControl label="Opens" value={h.open} onChange={(v, t) => set({ ...h, open: v }, t)} />
                  <TextControl label="Closes" value={h.close} onChange={(v, t) => set({ ...h, close: v }, t)} />
                </div>
              )}
            </>
          )}
        />
      )}

      {canEdit && <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-ink-500">Menu</h3>}
      {!canEdit ? null : translating ? (
        <div className="space-y-3">
          {site.nav.map((item, i) => (
            <TextControl key={item.page} label={item.label} value={item.labels[lang] ?? ""} placeholder={item.label}
              onChange={(v, t) => apply((d) => { if (v) d.site.nav[i].labels[lang] = v; else delete d.site.nav[i].labels[lang]; }, { coalesceKey: t ? `nav.${i}.${lang}` : undefined })} />
          ))}
        </div>
      ) : (
        <Repeater<Site["nav"][number]>
          label="Menu links"
          items={site.nav as Site["nav"]}
          onChange={(items) => apply(setNav(items))}
          makeBlank={() => {
            const unused = doc.pages.find((p) => !site.nav.some((n) => n.page === p.id)) ?? doc.pages[0];
            return { label: unused.title, page: unused.id, labels: {} };
          }}
          addLabel="Add link"
          renderItem={(item, set) => (
            <>
              <TextControl label="Label" value={item.label} onChange={(v, t) => set({ ...item, label: v }, t)} />
              <SelectControl label="Goes to" value={item.page} options={doc.pages.map((p) => ({ value: p.id, label: p.title }))} onChange={(v) => set({ ...item, page: v })} />
            </>
          )}
        />
      )}

      <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-ink-500">Footer</h3>
      {field("footer_text", "Footer text", true)}
      {canEdit && !translating && (
        <ToggleControl label="Show business info in footer" value={site.footer.show_business_info}
          onChange={(v) => apply((d) => { d.site.footer.show_business_info = v; })} />
      )}
    </div>
  );
}
