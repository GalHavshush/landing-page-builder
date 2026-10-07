import { describe, expect, it } from "vitest";
import { he } from "./locales/he";

const sources = import.meta.glob<string>("./**/*.{ts,tsx}", { query: "?raw", import: "default", eager: true });
const files = Object.entries(sources).filter(([f]) => !/generated|locales|\.test\./.test(f));

describe("Hebrew dictionary", () => {
  it("has an entry for every literal passed to t()", () => {
    const missing = new Set<string>();
    for (const [, text] of files)
      for (const m of text.matchAll(/\bt\(\s*"((?:[^"\\]|\\.)*)"/g)) {
        const key = m[1].replace(/\\"/g, '"');
        if (!(key in he)) missing.add(key);
      }
    expect([...missing]).toEqual([]);
  });
  it("keeps the same {placeholders} as the English text", () => {
    const names = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
    const bad = Object.entries(he).filter(([k, v]) => names(k).join() !== names(v).join()).map(([k]) => k);
    expect(bad).toEqual([]);
  });
});
