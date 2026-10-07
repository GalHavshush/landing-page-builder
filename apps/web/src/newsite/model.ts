/** The guided new-site form's state, its steps, and how a draft becomes the API's `Brief`. */
import type { components } from "@/api/generated/api";

type S = components["schemas"];
export type Brief = S["Brief"];
export type PageKind = NonNullable<Brief["pages"]>[number];
export type BusinessType = Brief["business_type"];
export type GoalKind = NonNullable<S["Goal"]["kind"]>;
export type Tf = (text: string, vars?: Record<string, string | number>) => string;

export const PAGE_ORDER: PageKind[] = ["about", "services", "pricing", "team", "faq"];
export const SOCIALS = ["instagram", "facebook", "tiktok", "linkedin"] as const;

/** Mirrors sitegen.brief.STARTER_FOR_TYPE (the server is the source of truth; this only labels the suggestion). */
export const STARTER_FOR_TYPE: Record<BusinessType, string> = {
  general: "clean", local_shop: "warm", restaurant: "restaurant", salon: "salon", trades: "trades",
  clinic: "clinic", photographer: "photographer", consultant: "consultant", fitness: "gym",
  garden: "landscaping", portfolio: "minimal",
};

export interface Draft {
  name: string;
  language: string;
  extra_languages: string[];
  business_type: BusinessType;
  template: string | null;
  tagline: string;
  description: string;
  goal: { kind: GoalKind; url: string };
  phone: string;
  email: string;
  address: string;
  hours: S["Hours"][];
  social: Record<string, string>;
  pages: PageKind[];
  primary: string | null;
  accent: string | null;
  headline: string;
  subheading: string;
  highlights: S["Highlight"][];
  stats: S["StatItem"][];
  testimonials: S["QuoteItem"][];
  story: string;
  services: S["ServiceItem"][];
  plans: S["PlanItem"][];
  team: S["MemberItem"][];
  faq: S["FaqEntry"][];
}

export const blank = {
  hours: (): S["Hours"] => ({ label: "", open: "", close: "", closed: false }),
  highlight: (): S["Highlight"] => ({ title: "", text: "" }),
  stat: (): S["StatItem"] => ({ value: "", label: "" }),
  quote: (): S["QuoteItem"] => ({ quote: "", author: "", role: "" }),
  service: (): S["ServiceItem"] => ({ title: "", description: "", price: "" }),
  plan: (): S["PlanItem"] => ({ name: "", price: "", period: "", features: "", highlighted: false }),
  member: (): S["MemberItem"] => ({ name: "", role: "", bio: "" }),
  faq: (): S["FaqEntry"] => ({ question: "", answer: "" }),
};
const many = <T,>(make: () => T, n: number) => Array.from({ length: n }, make);

export function initialDraft(language: string): Draft {
  return {
    name: "", language, extra_languages: [], business_type: "general", template: null, tagline: "", description: "",
    goal: { kind: "message", url: "" },
    phone: "", email: "", address: "", hours: [blank.hours()], social: {},
    pages: ["about", "services"], primary: null, accent: null,
    headline: "", subheading: "", highlights: many(blank.highlight, 3), stats: many(blank.stat, 3), testimonials: [blank.quote()],
    story: "", services: many(blank.service, 3), plans: [blank.plan()], team: [blank.member()], faq: many(blank.faq, 3),
  };
}

export type Group = "basics" | "pages" | "content" | "look";
export type StepId = "language" | "business" | "goal" | "contact" | "pages" | "home" | "proof" | PageKind | "look";
export interface Step { id: StepId; group: Group }

/** Steps for the pages the owner picked: content steps for unchosen pages are not shown. */
export function stepsFor(pages: PageKind[]): Step[] {
  return [
    { id: "language", group: "basics" }, { id: "business", group: "basics" }, { id: "goal", group: "basics" },
    { id: "contact", group: "basics" }, { id: "pages", group: "pages" },
    { id: "home", group: "content" }, { id: "proof", group: "content" },
    ...PAGE_ORDER.filter((p) => pages.includes(p)).map((id) => ({ id, group: "content" as const })),
    { id: "look", group: "look" },
  ];
}

/** Which generated page the live preview shows for a step. */
export function previewPage(step: StepId): string {
  if (step === "contact") return "pg_contact";
  return (PAGE_ORDER as string[]).includes(step) ? `pg_${step}` : "pg_home";
}

/** Why the step can't continue yet (an English message for the form's translator), or null. */
export function stepError(step: StepId, d: Draft): string | null {
  if (step === "business" && !d.name.trim()) return "Enter your business name";
  if (step === "goal" && d.goal.kind === "book" && !/^https:\/\/\S+$/i.test(d.goal.url.trim()))
    return "Enter a booking link that starts with https://";
  if (step === "contact") {
    if (d.email.trim() && !/^\S+@\S+\.\S+$/.test(d.email.trim())) return "Check the email address";
    if (Object.values(d.social).some((u) => u.trim() && !/^https?:\/\/\S+$/i.test(u.trim())))
      return "Social links must start with https://";
  }
  return null;
}

export function toBrief(d: Draft): Brief {
  const social = Object.fromEntries(Object.entries(d.social).filter(([, u]) => u.trim()).map(([k, u]) => [k, u.trim()]));
  return {
    name: d.name.trim() || "—",
    language: d.language,
    extra_languages: d.extra_languages.filter((c) => c !== d.language),
    business_type: d.business_type,
    template: d.template,
    tagline: d.tagline.trim(),
    description: d.description.trim(),
    goal: { kind: d.goal.kind, url: d.goal.kind === "book" ? d.goal.url.trim() : "" },
    business: {
      phone: d.phone.trim(), email: d.email.trim(), address: d.address.trim(),
      hours: d.hours.filter((h) => h.label.trim()), social,
    },
    pages: d.pages,
    palette: { primary: d.primary, accent: d.accent },
    headline: d.headline.trim(), subheading: d.subheading.trim(),
    highlights: d.highlights, stats: d.stats, testimonials: d.testimonials,
    story: d.story.trim(), services: d.services, plans: d.plans, team: d.team, faq: d.faq,
  };
}
