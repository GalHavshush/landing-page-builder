import type { Page } from "@/api/types";
import { setPageTranslation, updatePage, updatePageSeo } from "../commands";
import { TextAreaControl, TextControl, ToggleControl } from "../controls/basic";
import { ImageControl } from "../controls/ImageControl";
import { SlugControl } from "../controls/SlugControl";
import { currentPage, useCanEditStructure, useEditor } from "../store";
import { t } from "@/i18n";

type TField = "title" | "slug" | "seo_title" | "seo_description";

export function PagePanel() {
  const doc = useEditor((s) => s.doc)!;
  const page = useEditor(currentPage);
  const lang = useEditor((s) => s.lang)!;
  const apply = useEditor((s) => s.apply);
  const canEdit = useCanEditStructure();
  if (!page) return null;

  const translating = lang !== doc.site.default_language;
  const isHome = doc.pages[0].id === page.id;
  const tr = page.i18n[lang];
  const slugFor = (p: Page) => (translating ? (p.i18n[lang]?.slug ?? p.slug) : p.slug);
  const takenSlugs = doc.pages.filter((p) => p.id !== page.id).map(slugFor);

  const defaults: Record<TField, string> = {
    title: page.title, slug: page.slug, seo_title: page.seo.title ?? "", seo_description: page.seo.description ?? "",
  };
  const value = (f: TField) => (translating ? (tr?.[f] ?? "") : defaults[f]);
  const write = (f: TField, v: string, typing?: boolean) => {
    const key = typing ? `page.${page.id}.${f}.${lang}` : undefined;
    if (translating) apply(setPageTranslation(page.id, lang, f, v), { coalesceKey: key });
    else if (f === "title" || f === "slug") apply(updatePage(page.id, { [f]: v }), { coalesceKey: key });
    else apply(updatePageSeo(page.id, f === "seo_title" ? { title: v || null } : { description: v || null }), { coalesceKey: key });
  };
  const ph = (f: TField) => (translating ? defaults[f] : undefined);

  return (
    <div className="space-y-4">
      {translating && <p className="text-[12px] text-ink-600">{t("Translating this page. Empty fields use the default language.")}</p>}
      {canEdit && <TextControl label="Page title" value={value("title")} placeholder={ph("title")} onChange={(v, t) => write("title", v, t)} />}
      {canEdit && <SlugControl label="URL name" value={isHome ? "" : value("slug")} disabled={isHome} taken={takenSlugs}
        placeholder={ph("slug")} onChange={(v, t) => write("slug", v, t)} />}
      <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-ink-500">{t("Search engines")}</h3>
      <TextControl label="Search result title" value={value("seo_title")} placeholder={ph("seo_title") || page.title}
        hint="Leave empty to use the page title." ideal={60} max={200} onChange={(v, t) => write("seo_title", v, t)} />
      <TextAreaControl label="Search result description" value={value("seo_description")} placeholder={ph("seo_description")}
        hint="Shown under the title in search results." ideal={160} max={500} onChange={(v, t) => write("seo_description", v, t)} />
      {!translating && (
        <>
          <ImageControl label="Social sharing image"
            value={page.seo.social_image ? { asset: page.seo.social_image, alt: "", focus: { x: 50, y: 50 } } : null}
            onChange={(v) => apply(updatePageSeo(page.id, { social_image: v?.asset ?? null }))} />
          {canEdit && <ToggleControl label="Hide this page from search engines" value={page.seo.noindex}
            onChange={(v) => apply(updatePageSeo(page.id, { noindex: v }))} />}
        </>
      )}
    </div>
  );
}
