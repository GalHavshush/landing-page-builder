import { describe, expect, it } from "vitest";
import type { Section } from "@/api/types";
import { sectionSummary } from "./sectionSummary";

const sec = (props: object) => ({ id: "s", type: "x", variant: "v", props, style: {}, i18n: {} }) as unknown as Section;

describe("sectionSummary", () => {
  it("prefers the heading", () => expect(sectionSummary(sec({ heading: "Why us", eyebrow: "E" }))).toBe("Why us"));
  it("falls back to the first text", () => expect(sectionSummary(sec({ heading: "", body: "  Hello\n world " }))).toBe("Hello world"));
  it("describes a section that only has items", () =>
    expect(sectionSummary(sec({ heading: "", items: [{ quote: "Best meal all year", author: "M" }, { quote: "x" }] }))).toBe("Best meal all year +1"));
  it("uses a plan name and a button label", () => {
    expect(sectionSummary(sec({ plans: [{ name: "Pro" }] }))).toBe("Pro");
    expect(sectionSummary(sec({ buttons: [{ label: "Book now" }] }))).toBe("Book now");
  });
  it("is empty when there is nothing to say", () => expect(sectionSummary(sec({ heading: "", items: [] }))).toBe(""));
  it("truncates", () => expect(sectionSummary(sec({ heading: "x".repeat(80) }))).toHaveLength(40));
});
