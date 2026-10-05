/** Build a complete, readable palette from one brand colour. */
import { contrastRatio, MIN_CONTRAST } from "./contrast";

export type Palette = { primary: string; accent: string; background: string; surface: string; text: string };

function toHsl(hex: string): [number, number, number] {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2, d = max - min;
  if (d === 0) return [0, 0, l];
  const s = d / (1 - Math.abs(2 * l - 1));
  const h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return [(h * 60 + 360) % 360, s, l];
}

function fromHsl(h: number, s: number, l: number): string {
  h = ((h % 360) + 360) % 360;
  s = Math.min(1, Math.max(0, s));
  l = Math.min(1, Math.max(0, l));
  const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return "#" + [r, g, b].map((v) => Math.round((v + m) * 255).toString(16).padStart(2, "0")).join("").toUpperCase();
}

export function paletteFromBrand(brand: string, mode: "light" | "dark" = "light"): Palette {
  const [h, s] = toHsl(brand);
  const tint = Math.min(s, 0.35); // keep neutrals only lightly tinted by the brand hue
  const accent = fromHsl(h + 150, Math.max(0.6, Math.min(s, 0.85)), 0.55);
  const p: Palette =
    mode === "light"
      ? { primary: brand.toUpperCase(), accent, background: fromHsl(h, tint * 0.5, 0.99), surface: fromHsl(h, tint, 0.95), text: fromHsl(h, tint, 0.1) }
      : { primary: brand.toUpperCase(), accent, background: fromHsl(h, tint, 0.08), surface: fromHsl(h, tint, 0.13), text: fromHsl(h, tint * 0.6, 0.95) };
  // Safety net: push the text colour to the extreme if the pair is somehow too close.
  for (const bg of [p.background, p.surface]) {
    if (contrastRatio(p.text, bg) < MIN_CONTRAST) p.text = mode === "light" ? "#111111" : "#F5F5F5";
  }
  return p;
}
