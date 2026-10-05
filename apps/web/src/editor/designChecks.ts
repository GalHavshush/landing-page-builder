/** Friendly "does this look right?" checks that run in the editor on the current document. */
import type { Section, SiteDocument } from "@/api/types";
import { t } from "@/i18n";

export type Check = { pageId: string; sectionId: string | null; level: "warn" | "tip"; message: string };

type Props = Record<string, unknown>;
const LISTS = ["items", "plans", "buttons"] as const;
const GRID_TYPES = new Set(["features", "services", "team", "testimonials", "stats", "logos"]);
const hasImage = (v: unknown) => !!v && typeof v === "object" && !!(v as { asset?: string }).asset;

function sectionChecks(pageId: string, s: Section): Check[] {
  const props = s.props as unknown as Props;
  const out: Check[] = [];
  const add = (level: Check["level"], message: string) => out.push({ pageId, sectionId: s.id, level, message });
  const heading = typeof props.heading === "string" ? props.heading.trim() : "";
  const limit = s.type === "hero" ? 90 : 60;
  if (heading.length > limit) add("tip", t("The heading is long ({n} characters). Shorter headings read better, aim for under {limit}.", { n: heading.length, limit }));

  const listProp = LISTS.find((k) => Array.isArray(props[k]) && k !== "buttons");
  if (listProp && (props[listProp] as unknown[]).length === 0 && s.type !== "blog_list")
    add("warn", t("This section is empty. Add an item or remove the section."));
  if (GRID_TYPES.has(s.type) && Array.isArray(props.items) && props.items.length === 1 && s.type !== "testimonials")
    add("tip", t("Only one item. Add at least two or three so it reads as a set."));
  if (s.type === "hero" && (s.variant === "cover" || s.variant === "banner") && hasImage(props.image) && props.overlay === "none")
    add("warn", t("Text sits directly on a photo with no darkening. Choose a Light, Dark or Heavy overlay so it stays readable."));
  if (s.type === "hero" && s.variant === "cover" && !hasImage(props.image) && !props.video_url)
    add("tip", t("A Cover hero needs a photo or video to fill the background."));
  if (s.type === "services" && Array.isArray(props.items) && props.items.length > 0) {
    const withImg = props.items.filter((i: { image?: unknown }) => hasImage(i.image)).length;
    if (withImg > 0 && withImg < props.items.length) add("tip", t("Some items have a photo and some do not, which looks uneven."));
  }
  return out;
}

export function designChecks(doc: SiteDocument): Check[] {
  const out: Check[] = [];
  for (const page of doc.pages) {
    let primaryButtons = 0;
    page.sections.forEach((s, i) => {
      out.push(...sectionChecks(page.id, s));
      const btns = (s.props as unknown as Props).buttons;
      if (Array.isArray(btns)) primaryButtons += btns.filter((b: { style?: string }) => (b.style ?? "primary") === "primary").length;
      if (i > 0 && s.style.background === page.sections[i - 1].style.background && s.style.background !== "default")
        out.push({ pageId: page.id, sectionId: s.id, level: "tip", message: t("Two sections in a row share the same tinted background, so they run together.") });
    });
    if (primaryButtons > 3)
      out.push({ pageId: page.id, sectionId: null, level: "tip", message: t("{n} main buttons on one page. Too many calls to action dilute each other. Make some of them outline or link buttons.", { n: primaryButtons }) });
    if (page.sections.length > 10)
      out.push({ pageId: page.id, sectionId: null, level: "tip", message: t("This is a very long page. Consider splitting it into two.") });
  }
  return out;
}
