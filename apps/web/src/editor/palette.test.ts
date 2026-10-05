import { describe, expect, it } from "vitest";
import { contrastRatio, isHex, MIN_CONTRAST } from "./contrast";
import { paletteFromBrand } from "./palette";

describe("paletteFromBrand", () => {
  const brands = ["#2563EB", "#B4532A", "#2F6F4F", "#BE185D", "#FACC15", "#111827", "#FFFFFF", "#00FF00"];
  for (const mode of ["light", "dark"] as const) {
    it.each(brands)(`gives a valid, readable ${mode} palette for %s`, (brand) => {
      const p = paletteFromBrand(brand, mode);
      for (const v of Object.values(p)) expect(isHex(v)).toBe(true);
      expect(p.primary).toBe(brand.toUpperCase());
      expect(contrastRatio(p.text, p.background)).toBeGreaterThanOrEqual(MIN_CONTRAST);
      expect(contrastRatio(p.text, p.surface)).toBeGreaterThanOrEqual(MIN_CONTRAST);
    });
  }
});
