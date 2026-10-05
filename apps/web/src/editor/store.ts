import { create } from "zustand";
import type { Page, SiteDocument } from "@/api/types";

export type Device = "desktop" | "mobile";

interface EditorState {
  projectId: number | null;
  doc: SiteDocument | null;
  revision: number;
  pageId: string | null;
  lang: string | null;
  selectedId: string | null;
  device: Device;

  load: (projectId: number, doc: SiteDocument, revision: number) => void;
  selectPage: (pageId: string) => void;
  selectSection: (id: string | null) => void;
  setDevice: (d: Device) => void;
  setLang: (lang: string) => void;
}

export const useEditor = create<EditorState>((set) => ({
  projectId: null,
  doc: null,
  revision: 0,
  pageId: null,
  lang: null,
  selectedId: null,
  device: "desktop",

  load: (projectId, doc, revision) =>
    set({
      projectId,
      doc,
      revision,
      pageId: doc.pages[0]?.id ?? null,
      lang: doc.site.default_language,
      selectedId: null,
    }),
  selectPage: (pageId) => set({ pageId, selectedId: null }),
  selectSection: (selectedId) => set({ selectedId }),
  setDevice: (device) => set({ device }),
  setLang: (lang) => set({ lang }),
}));

export function currentPage(state: Pick<EditorState, "doc" | "pageId">): Page | undefined {
  return state.doc?.pages.find((p) => p.id === state.pageId);
}
