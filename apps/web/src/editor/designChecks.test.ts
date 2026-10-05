import { describe, expect, it } from "vitest";
import type { SiteDocument } from "@/api/types";
import { designChecks } from "./designChecks";

const sec = (id: string, type: string, props: object, extra: object = {}) =>
  ({ id, type, variant: "x", i18n: {}, style: { background: "default", spacing: "normal", align: "start" }, props, ...extra }) as never;
const doc = (...sections: never[]) => ({ pages: [{ id: "p", title: "Home", slug: "", sections }] }) as unknown as SiteDocument;

describe("designChecks", () => {
  it("is quiet for a healthy page", () => {
    expect(designChecks(doc(sec("a", "features", { heading: "Why us", items: [{}, {}, {}] })))).toEqual([]);
  });
  it("flags long headings, empty sections and single-item grids", () => {
    const out = designChecks(doc(
      sec("a", "text", { heading: "x".repeat(80), body: "" }),
      sec("b", "services", { heading: "S", items: [] }),
      sec("c", "features", { heading: "F", items: [{}] }),
    ));
    expect(out.map((c) => c.sectionId)).toEqual(["a", "b", "c"]);
    expect(out.find((c) => c.sectionId === "b")?.level).toBe("warn");
  });
  it("flags unreadable text over a photo", () => {
    const hero = sec("h", "hero", { heading: "Hi", image: { asset: "a1" }, overlay: "none", buttons: [] }, { variant: "cover" });
    expect(designChecks(doc(hero))[0].message).toMatch(/overlay/i);
  });
  it("flags too many primary buttons on a page", () => {
    const b = { label: "x", style: "primary" };
    const out = designChecks(doc(sec("a", "hero", { heading: "H", buttons: [b, b] }), sec("b", "cta", { heading: "C", buttons: [b, b] })));
    expect(out.some((c) => c.sectionId === null && /main buttons/.test(c.message))).toBe(true);
  });
  it("flags adjacent tinted sections", () => {
    const tinted = (id: string) => sec(id, "text", { heading: "T" }, { style: { background: "alt", spacing: "normal", align: "start" } });
    expect(designChecks(doc(tinted("a"), tinted("b")))[0].sectionId).toBe("b");
  });
});
