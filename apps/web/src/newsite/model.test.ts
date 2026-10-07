import { describe, expect, it } from "vitest";
import { he } from "@/locales/he";
import { initialDraft, previewPage, stepError, stepsFor, toBrief } from "./model";
import { GOALS, PAGE_INFO, STEP_VIEW, TYPE_LABELS } from "./steps";

const sources = import.meta.glob<string>(["./*.{ts,tsx}", "../pages/NewSite.tsx"], { query: "?raw", import: "default", eager: true });

describe("form text", () => {
  it("has Hebrew for every string the form can show", () => {
    const keys = new Set<string>([
      ...Object.values(STEP_VIEW).flatMap((s) => [s.title, s.help]),
      ...TYPE_LABELS.map(([, l]) => l),
      ...GOALS.flatMap(([, l, h]) => [l, h]),
      ...Object.values(PAGE_INFO).flat(),
    ]);
    for (const [, text] of Object.entries(sources).filter(([f]) => !f.endsWith(".test.ts")))
      for (const m of text.matchAll(/\bT\(\s*"((?:[^"\\]|\\.)*)"/g)) keys.add(m[1].replace(/\\"/g, '"'));
    for (const m of sources["./model.ts"].matchAll(/return "([A-Z][^"]+)"/g)) keys.add(m[1]); // step errors
    expect([...keys].filter((k) => !(k in he))).toEqual([]);
  });
});

describe("steps", () => {
  it("only asks about the pages that were picked", () => {
    const ids = (pages: Parameters<typeof stepsFor>[0]) => stepsFor(pages).map((s) => s.id);
    expect(ids([])).toEqual(["language", "business", "goal", "contact", "pages", "home", "proof", "look"]);
    expect(ids(["faq", "about"])).toEqual(expect.arrayContaining(["about", "faq"]));
    expect(ids(["faq", "about"]).indexOf("about")).toBeLessThan(ids(["faq", "about"]).indexOf("faq"));
  });
  it("previews the page being edited", () => {
    expect(previewPage("services")).toBe("pg_services");
    expect(previewPage("contact")).toBe("pg_contact");
    expect(previewPage("proof")).toBe("pg_home");
  });
});

describe("validation and payload", () => {
  it("requires a name, a booking link for online booking, and sane contact info", () => {
    const d = initialDraft("en");
    expect(stepError("business", d)).toBeTruthy();
    expect(stepError("business", { ...d, name: "Rosa" })).toBeNull();
    expect(stepError("goal", { ...d, goal: { kind: "book", url: "cal.com/x" } })).toBeTruthy();
    expect(stepError("goal", { ...d, goal: { kind: "book", url: "https://cal.com/x" } })).toBeNull();
    expect(stepError("contact", { ...d, email: "nope" })).toBeTruthy();
    expect(stepError("contact", { ...d, social: { instagram: "insta" } })).toBeTruthy();
    expect(stepError("contact", d)).toBeNull();
  });
  it("sends only what was filled in", () => {
    const d = { ...initialDraft("he"), name: " Rosa ", social: { instagram: "https://i.example/r", tiktok: " " }, primary: "#112233" };
    const b = toBrief(d);
    expect(b.name).toBe("Rosa");
    expect(b.language).toBe("he");
    expect(b.business?.social).toEqual({ instagram: "https://i.example/r" });
    expect(b.business?.hours).toEqual([]); // the blank starter row is dropped
    expect(b.palette).toEqual({ primary: "#112233", accent: null });
    expect(b.goal).toEqual({ kind: "message", url: "" });
  });
});
