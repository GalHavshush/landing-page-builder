/** Light / dark / follow-the-system, remembered in localStorage and applied as data-theme on <html>. */
import { useSyncExternalStore } from "react";

export type ThemePref = "system" | "light" | "dark";
const KEY = "theme";

export const resolveTheme = (pref: ThemePref, systemDark: boolean): "light" | "dark" =>
  pref === "system" ? (systemDark ? "dark" : "light") : pref;

export function readPref(): ThemePref {
  try {
    const v = localStorage.getItem(KEY);
    return v === "light" || v === "dark" ? v : "system";
  } catch {
    return "system"; // storage can be blocked (private windows)
  }
}

const systemQuery = () => window.matchMedia("(prefers-color-scheme: dark)");
const listeners = new Set<() => void>();
let pref: ThemePref = "system";

export function applyTheme() {
  document.documentElement.dataset.theme = resolveTheme(pref, systemQuery().matches);
}

export function setThemePref(next: ThemePref) {
  pref = next;
  try {
    if (next === "system") localStorage.removeItem(KEY);
    else localStorage.setItem(KEY, next);
  } catch {
    /* not persisted, still applied */
  }
  applyTheme();
  listeners.forEach((l) => l());
}

/** Call once at startup: applies the saved preference and follows OS changes while on "system". */
export function initTheme() {
  pref = readPref();
  applyTheme();
  systemQuery().addEventListener("change", () => pref === "system" && applyTheme());
}

export function useThemePref(): ThemePref {
  return useSyncExternalStore(
    (cb) => (listeners.add(cb), () => listeners.delete(cb)),
    () => pref,
  );
}
