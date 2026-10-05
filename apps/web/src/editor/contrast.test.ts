import { describe, expect, it } from "vitest";
import { contrastRatio, isHex } from "./contrast";

describe("contrast", () => {
  it("matches the known WCAG extremes", () => {
    expect(contrastRatio("#000000", "#FFFFFF")).toBeCloseTo(21, 0);
    expect(contrastRatio("#777777", "#777777")).toBeCloseTo(1, 5);
  });
  it("flags light grey on white as insufficient", () => {
    expect(contrastRatio("#BBBBBB", "#FFFFFF")).toBeLessThan(4.5);
    expect(contrastRatio("#111827", "#FFFFFF")).toBeGreaterThan(4.5);
  });
  it("validates hex colors like the server", () => {
    expect(isHex("#2563EB")).toBe(true);
    expect(isHex("#fff")).toBe(false);
    expect(isHex("blue")).toBe(false);
  });
});
