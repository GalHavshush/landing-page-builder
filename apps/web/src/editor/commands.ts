/**
 * Every change to the document is one of these small pure functions (a "recipe" that mutates an
 * Immer draft). The store runs them through Immer, which records patches for undo/redo.
 * Keeping edits as named commands makes them easy to test and to reason about.
 */
import type { Draft } from "immer";
import type { Page, Section, SiteDocument } from "@/api/types";

export type Recipe = (draft: Draft<SiteDocument>) => void;

export function newId(prefix: string): string {
  return `${prefix}_${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`;
}

export function slugify(text: string): string {
  return text.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function locate(doc: Draft<SiteDocument>, sectionId: string) {
  for (const page of doc.pages) {
    const index = page.sections.findIndex((s) => s.id === sectionId);
    if (index !== -1) return { page, index, section: page.sections[index] };
  }
  throw new Error(`section ${sectionId} not found`);
}

export const addSection =
  (pageId: string, section: Section, index?: number): Recipe =>
  (doc) => {
    const page = doc.pages.find((p) => p.id === pageId);
    if (!page) throw new Error(`page ${pageId} not found`);
    page.sections.splice(index ?? page.sections.length, 0, section as Draft<Section>);
  };

export const removeSection =
  (sectionId: string): Recipe =>
  (doc) => {
    const { page, index } = locate(doc, sectionId);
    page.sections.splice(index, 1);
  };

/** Move a section to `toIndex` within its page (index in the list as it is before the move). */
export const moveSection =
  (sectionId: string, toIndex: number): Recipe =>
  (doc) => {
    const { page, index } = locate(doc, sectionId);
    const [item] = page.sections.splice(index, 1);
    page.sections.splice(Math.max(0, Math.min(toIndex, page.sections.length)), 0, item);
  };

export const duplicateSection =
  (sectionId: string, newSectionId: string = newId("sec")): Recipe =>
  (doc) => {
    const { page, index, section } = locate(doc, sectionId);
    const copy = JSON.parse(JSON.stringify(section)) as Draft<Section>;
    copy.id = newSectionId;
    page.sections.splice(index + 1, 0, copy);
  };

export const updateProps =
  (sectionId: string, patch: Record<string, unknown>): Recipe =>
  (doc) => {
    Object.assign(locate(doc, sectionId).section.props, patch);
  };

export const setVariant =
  (sectionId: string, variant: string): Recipe =>
  (doc) => {
    (locate(doc, sectionId).section as { variant: string }).variant = variant;
  };

export const updateStyle =
  (sectionId: string, patch: Partial<Section["style"]>): Recipe =>
  (doc) => {
    Object.assign(locate(doc, sectionId).section.style, patch);
  };

/** Set (or clear, with undefined) a translated value for one content prop. */
export const setTranslation =
  (sectionId: string, lang: string, prop: string, value: unknown): Recipe =>
  (doc) => {
    const section = locate(doc, sectionId).section;
    const bucket = (section.i18n[lang] ??= {});
    if (value === undefined) delete bucket[prop];
    else bucket[prop] = value;
    if (Object.keys(bucket).length === 0) delete section.i18n[lang];
  };

export const addPage =
  (title: string, id: string = newId("pg"), sections: Section[] = []): Recipe =>
  (doc) => {
    const taken = new Set(doc.pages.map((p) => p.slug));
    const base = slugify(title) || "page";
    let slug = base;
    for (let n = 2; taken.has(slug); n++) slug = `${base}-${n}`;
    const page: Page = { id, slug, title, seo: { title: null, description: null, social_image: null, noindex: false }, sections: sections.map((s) => ({ ...structuredClone(s), id: newId("sec") })), i18n: {} };
    doc.pages.push(page as Draft<Page>);
    doc.site.nav.push({ label: title, page: id, labels: {} });
  };

export const removePage =
  (pageId: string): Recipe =>
  (doc) => {
    if (doc.pages.length <= 1) throw new Error("a site needs at least one page");
    doc.pages = doc.pages.filter((p) => p.id !== pageId);
    // the server rejects navigation items that point at missing pages
    doc.site.nav = doc.site.nav.filter((n) => n.page !== pageId);
  };

export const updatePage =
  (pageId: string, patch: Partial<Pick<Page, "title" | "slug">>): Recipe =>
  (doc) => {
    const page = doc.pages.find((p) => p.id === pageId);
    if (page) Object.assign(page, patch);
  };

export const updateSite =
  (patch: Partial<SiteDocument["site"]>): Recipe =>
  (doc) => {
    Object.assign(doc.site, patch);
  };

export const updateTheme =
  (patch: Partial<SiteDocument["theme"]>): Recipe =>
  (doc) => {
    Object.assign(doc.theme, patch);
  };

// ---- page / site settings, navigation and languages -------------------------------------

type PageSeo = Page["seo"];

export const updatePageSeo =
  (pageId: string, patch: Partial<PageSeo>): Recipe =>
  (doc) => {
    const page = doc.pages.find((p) => p.id === pageId);
    if (page) Object.assign(page.seo, patch);
  };

/** Set (or clear, with undefined) one translated page field: title, slug, seo_title, seo_description. */
export const setPageTranslation =
  (pageId: string, lang: string, field: "title" | "slug" | "seo_title" | "seo_description", value: string | undefined): Recipe =>
  (doc) => {
    const page = doc.pages.find((p) => p.id === pageId);
    if (!page) return;
    const bucket = (page.i18n[lang] ??= { title: null, slug: null, seo_title: null, seo_description: null });
    bucket[field] = value === undefined || value === "" ? null : value;
    if (Object.values(bucket).every((v) => v === null)) delete page.i18n[lang];
  };

export const setSiteTranslation =
  (lang: string, field: "name" | "tagline" | "description" | "address" | "footer_text" | "cta_label" | "announcement_text", value: string | undefined): Recipe =>
  (doc) => {
    const bucket = (doc.site.i18n[lang] ??= { name: null, tagline: null, description: null, address: null, hours: null, footer_text: null, cta_label: null, announcement_text: null });
    bucket[field] = value === undefined || value === "" ? null : value;
    if (Object.values(bucket).every((v) => v === null)) delete doc.site.i18n[lang];
  };

export const setNav =
  (nav: SiteDocument["site"]["nav"]): Recipe =>
  (doc) => {
    doc.site.nav = nav as Draft<SiteDocument["site"]["nav"]>;
  };

export const addLanguage =
  (code: string): Recipe =>
  (doc) => {
    if (!doc.site.languages.includes(code)) doc.site.languages.push(code);
  };

/** Remove a language and every translation of it (the server rejects dangling translations). */
export const removeLanguage =
  (code: string): Recipe =>
  (doc) => {
    if (code === doc.site.default_language) throw new Error("cannot remove the default language");
    doc.site.languages = doc.site.languages.filter((l) => l !== code);
    delete doc.site.i18n[code];
    for (const item of doc.site.nav) delete item.labels[code];
    for (const page of doc.pages) {
      delete page.i18n[code];
      for (const section of page.sections) delete section.i18n[code];
    }
  };

/**
 * Give a page's sections an even rhythm: plain and tinted backgrounds alternate, while coloured
 * (primary/dark) sections and cover heroes are left alone and restart the alternation.
 */
export const balanceBackgrounds =
  (): Recipe =>
  (doc) => {
    for (const page of doc.pages) {
      let tinted = false;
      for (const s of page.sections) {
        const bold = s.style.background === "primary" || s.style.background === "dark";
        const cover = s.type === "hero" && (s.variant === "cover" || s.variant === "banner");
        if (bold || cover) { tinted = false; continue; }
        s.style.background = tinted ? "alt" : "default";
        tinted = !tinted;
      }
    }
  };
