import type { Section } from "@/api/types";

const TEXT_KEYS = ["heading", "eyebrow", "caption", "body", "text", "url", "query"] as const;
const ITEM_KEYS = ["title", "name", "quote", "question", "label", "value", "alt"] as const;

const clean = (v: unknown) => (typeof v === "string" ? v.replace(/\s+/g, " ").trim() : "");

/** A short line for the section list: its heading, else its first text, else what its first item says. */
export function sectionSummary(section: Section, max = 40): string {
  const p = section.props as unknown as Record<string, unknown>;
  for (const k of TEXT_KEYS) {
    const t = clean(p[k]);
    if (t) return t.slice(0, max);
  }
  for (const list of ["items", "plans", "buttons"] as const) {
    const items = p[list];
    if (Array.isArray(items) && items.length) {
      const first = items[0] as Record<string, unknown>;
      for (const k of ["name", ...ITEM_KEYS]) {
        const t = clean(first?.[k]);
        if (t) return `${t.slice(0, max - 8)}${items.length > 1 ? ` +${items.length - 1}` : ""}`;
      }
    }
  }
  return "";
}
