import { describe, expect, it } from "vitest";
import { insertAt, makeLink, prefixLines, wrap } from "./markdown";

describe("markdown edits", () => {
  it("wraps a selection and selects the inner text", () => {
    const e = wrap("hello world", 6, 11, "**");
    expect(e.text).toBe("hello **world**");
    expect(e.text.slice(e.start, e.end)).toBe("world");
  });
  it("uses a placeholder without a selection", () => {
    const e = wrap("", 0, 0, "*");
    expect(e.text).toBe("*text*");
    expect(e.text.slice(e.start, e.end)).toBe("text");
  });
  it("toggles off when already wrapped", () => {
    const e = wrap("a **b** c", 4, 5, "**");
    expect(e.text).toBe("a b c");
  });
  it("prefixes every selected line and toggles back", () => {
    const e = prefixLines("one\ntwo\nthree", 0, 7, "- ");
    expect(e.text).toBe("- one\n- two\nthree");
    expect(prefixLines(e.text, e.start, e.end, "- ").text).toBe("one\ntwo\nthree");
  });
  it("replaces another list/heading marker instead of stacking", () => {
    expect(prefixLines("## Title", 0, 3, "- ").text).toBe("- Title");
  });
  it("numbers ordered lists", () => {
    expect(prefixLines("a\nb", 0, 3, (i) => `${i + 1}. `).text).toBe("1. a\n2. b");
  });
  it("makes links and selects the url", () => {
    const e = makeLink("see docs", 4, 8);
    expect(e.text).toBe("see [docs](https://)");
    expect(e.text.slice(e.start, e.end)).toBe("https://");
  });
  it("inserts a block on its own line", () => {
    expect(insertAt("para", 4, "![x](asset:a)").text).toBe("para\n\n![x](asset:a)\n");
    expect(insertAt("", 0, "![x](asset:a)").text).toBe("![x](asset:a)\n");
  });
});
