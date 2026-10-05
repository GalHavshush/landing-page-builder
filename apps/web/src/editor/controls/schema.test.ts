import { describe, expect, it } from "vitest";
import { blankItem, itemTitle, unwrap } from "./schema";

const defs = {
  Link: { type: "object", properties: { page: { type: "string" } } },
  Feature: {
    type: "object",
    properties: {
      icon: { anyOf: [{ enum: ["star"], type: "string" }, { type: "null" }], default: null, control: "icon" },
      title: { type: "string", default: "", control: "text" },
      count: { type: "integer" },
      link: { anyOf: [{ $ref: "#/$defs/Link" }, { type: "null" }], default: null, control: "link" },
    },
  },
};

describe("schema helpers", () => {
  it("unwraps $ref and Optional while keeping wrapper hints", () => {
    const s = unwrap(defs.Feature.properties.link, defs);
    expect(s.control).toBe("link");
    expect(s.type).toBe("object");
    expect(unwrap(defs.Feature.properties.icon, defs).enum).toEqual(["star"]);
  });
  it("builds blank items from defaults", () => {
    expect(blankItem({ $ref: "#/$defs/Feature" }, defs)).toEqual({ icon: null, title: "", count: null, link: null });
  });
  it("names items by their first descriptive field", () => {
    expect(itemTitle({ title: "Quality" }, 0)).toBe("Quality");
    expect(itemTitle({ question: "Why?" }, 1)).toBe("Why?");
    expect(itemTitle({}, 2)).toBe("Item 3");
  });
});
