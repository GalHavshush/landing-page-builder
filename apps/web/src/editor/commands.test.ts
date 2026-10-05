import { produce } from "immer";
import { describe, expect, it } from "vitest";
import type { SiteDocument } from "@/api/types";
import * as c from "./commands";

const section = (id: string, heading = id) =>
  ({
    id,
    type: "text",
    variant: "single",
    style: { background: "default", spacing: "normal", align: "start" },
    i18n: {},
    props: { heading, body: "" },
  }) as unknown as SiteDocument["pages"][number]["sections"][number];

function doc(): SiteDocument {
  return {
    schema_version: 1,
    site: { name: "T", nav: [{ label: "Home", page: "p1", labels: {} }, { label: "B", page: "p2", labels: {} }], default_language: "en", languages: ["en"], i18n: {} },
    theme: {},
    pages: [
      { id: "p1", slug: "", title: "Home", seo: {}, i18n: {}, sections: [section("a"), section("b"), section("c")] },
      { id: "p2", slug: "b", title: "B", seo: {}, i18n: {}, sections: [] },
    ],
  } as unknown as SiteDocument;
}
const run = (d: SiteDocument, r: c.Recipe) => produce(d, r);
const ids = (d: SiteDocument, p = 0) => d.pages[p].sections.map((s) => s.id);

describe("section commands", () => {
  it("adds at an index and at the end", () => {
    expect(ids(run(doc(), c.addSection("p1", section("x"), 1)))).toEqual(["a", "x", "b", "c"]);
    expect(ids(run(doc(), c.addSection("p2", section("x"))), 1)).toEqual(["x"]);
  });
  it("removes", () => expect(ids(run(doc(), c.removeSection("b")))).toEqual(["a", "c"]));
  it("moves up and down", () => {
    expect(ids(run(doc(), c.moveSection("a", 2)))).toEqual(["b", "c", "a"]);
    expect(ids(run(doc(), c.moveSection("c", 0)))).toEqual(["c", "a", "b"]);
  });
  it("duplicates with a new id right after the original", () => {
    const d = run(doc(), c.duplicateSection("a", "a2"));
    expect(ids(d)).toEqual(["a", "a2", "b", "c"]);
    expect(d.pages[0].sections[1]).not.toBe(d.pages[0].sections[0]);
  });
  it("updates props, variant and style", () => {
    const d = run(run(run(doc(), c.updateProps("a", { heading: "Hi" })), c.setVariant("a", "columns")), c.updateStyle("a", { align: "center" }));
    expect(d.pages[0].sections[0]).toMatchObject({ variant: "columns", style: { align: "center" }, props: { heading: "Hi" } });
  });
  it("sets and clears translations", () => {
    const d1 = run(doc(), c.setTranslation("a", "he", "heading", "שלום"));
    expect(d1.pages[0].sections[0].i18n).toEqual({ he: { heading: "שלום" } });
    const d2 = run(d1, c.setTranslation("a", "he", "heading", undefined));
    expect(d2.pages[0].sections[0].i18n).toEqual({});
  });
  it("throws for unknown sections", () => expect(() => run(doc(), c.removeSection("zz"))).toThrow());
});

describe("page commands", () => {
  it("adds a page with a unique slug and a nav item", () => {
    const d = run(run(doc(), c.addPage("About us", "p3")), c.addPage("About us", "p4"));
    expect(d.pages.map((p) => p.slug)).toEqual(["", "b", "about-us", "about-us-2"]);
    expect(d.site.nav.map((n) => n.page)).toEqual(["p1", "p2", "p3", "p4"]);
  });
  it("removing a page removes its nav item (the server rejects dangling nav)", () => {
    const d = run(doc(), c.removePage("p2"));
    expect(d.pages.map((p) => p.id)).toEqual(["p1"]);
    expect(d.site.nav.map((n) => n.page)).toEqual(["p1"]);
  });
  it("refuses to delete the last page", () => {
    expect(() => run(run(doc(), c.removePage("p2")), c.removePage("p1"))).toThrow();
  });
});

describe("language and settings commands", () => {
  const multi = () => {
    const d = doc();
    d.site.languages = ["en", "he"];
    d.site.nav[0].labels = { he: "בית" };
    d.pages[0].i18n = { he: { title: "בית", slug: null, seo_title: null, seo_description: null } } as never;
    d.pages[0].sections[0].i18n = { he: { heading: "שלום" } };
    d.site.i18n = { he: { name: "ת", tagline: null, description: null, address: null, hours: null, footer_text: null } } as never;
    return d;
  };
  it("adds a language once", () => {
    const d = run(run(doc(), c.addLanguage("he")), c.addLanguage("he"));
    expect(d.site.languages).toEqual(["en", "he"]);
  });
  it("removing a language deletes every translation of it", () => {
    const d = run(multi(), c.removeLanguage("he"));
    expect(d.site.languages).toEqual(["en"]);
    expect(d.site.i18n).toEqual({});
    expect(d.site.nav[0].labels).toEqual({});
    expect(d.pages[0].i18n).toEqual({});
    expect(d.pages[0].sections[0].i18n).toEqual({});
    expect(JSON.stringify(d)).not.toContain("שלום");
  });
  it("cannot remove the default language", () => {
    expect(() => run(doc(), c.removeLanguage("en"))).toThrow();
  });
  it("page and site translations are cleaned up when emptied", () => {
    const a = run(doc(), c.setPageTranslation("p1", "he", "title", "בית"));
    expect(a.pages[0].i18n.he.title).toBe("בית");
    expect(run(a, c.setPageTranslation("p1", "he", "title", "")).pages[0].i18n).toEqual({});
    const b = run(doc(), c.setSiteTranslation("he", "name", "ת"));
    expect(run(b, c.setSiteTranslation("he", "name", undefined)).site.i18n).toEqual({});
  });
});

describe("balanceBackgrounds", () => {
  it("alternates plain and tinted, restarting after bold sections", () => {
    const mk = (type: string, background: string, variant = "") =>
      ({ id: type + background + Math.random(), type, variant, props: {}, style: { background, align: "start", spacing: "normal" } }) as never;
    const doc = {
      pages: [{ sections: [mk("text", "alt"), mk("text", "alt"), mk("cta", "primary"), mk("text", "alt"), mk("text", "default"), mk("text", "default")] }],
    } as never;
    const next = produce(doc as unknown as SiteDocument, c.balanceBackgrounds());
    expect(next.pages[0].sections.map((s) => s.style.background)).toEqual(
      ["default", "alt", "primary", "default", "alt", "default"],
    );
  });
});
