/**
 * Editor (not website) language. Strings are keyed by their English text, so `t("Save")` returns the
 * English as-is and the Hebrew from locales/he.ts when that is the chosen language. Changing the
 * language remounts the app (see main.tsx), so t() can be a plain function called while rendering.
 */
import { useSyncExternalStore } from "react";
import { he } from "./locales/he";

export type UiLang = "en" | "he";
export const UI_LANGUAGES: { value: UiLang; label: string }[] = [
  { value: "en", label: "English" },
  { value: "he", label: "עברית" },
];
const KEY = "ui-language";
const DICTS: Record<UiLang, Record<string, string>> = { en: {}, he };
const listeners = new Set<() => void>();

const read = (): UiLang => {
  try {
    return localStorage.getItem(KEY) === "he" ? "he" : "en";
  } catch {
    return "en"; // storage can be blocked
  }
};
let lang: UiLang = read();

export const getUiLang = () => lang;
export const isRtl = (l: UiLang = lang) => l === "he";

export function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = isRtl() ? "rtl" : "ltr";
}

export function setUiLang(next: UiLang) {
  if (next === lang) return;
  lang = next;
  try {
    localStorage.setItem(KEY, next);
  } catch {
    /* applied, just not remembered */
  }
  applyLang();
  listeners.forEach((l) => l());
}

export function useUiLang(): UiLang {
  return useSyncExternalStore(
    (cb) => (listeners.add(cb), () => listeners.delete(cb)),
    () => lang,
  );
}

/** Translate an English UI string; `{name}` placeholders are filled from `vars`. */
export function t(text: string, vars?: Record<string, string | number>): string {
  const out = DICTS[lang][text] ?? text;
  return vars ? out.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : out;
}
