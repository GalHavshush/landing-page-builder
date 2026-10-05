import { enablePatches, produceWithPatches, applyPatches, type Patch } from "immer";
import { create } from "zustand";
import type { Page, SiteDocument } from "@/api/types";
import type { Recipe } from "./commands";

enablePatches();

export type Device = "desktop" | "mobile";
export type SaveStatus = "saved" | "dirty" | "saving" | "error" | "conflict" | "invalid";

interface HistoryEntry {
  patches: Patch[];
  inverse: Patch[];
  key?: string; // consecutive edits with the same key (typing in one field) merge into one entry
  at: number;
}

const COALESCE_MS = 1200;
const MAX_HISTORY = 200;

interface EditorState {
  projectId: number | null;
  doc: SiteDocument | null;
  savedDoc: SiteDocument | null; // last version the server acknowledged
  revision: number;
  saveStatus: SaveStatus;
  saveError: string | null;
  undoStack: HistoryEntry[];
  redoStack: HistoryEntry[];
  pageId: string | null;
  lang: string | null;
  selectedId: string | null;
  device: Device;

  load: (projectId: number, doc: SiteDocument, revision: number) => void;
  apply: (recipe: Recipe, opts?: { coalesceKey?: string }) => void;
  undo: () => void;
  redo: () => void;
  selectPage: (pageId: string) => void;
  selectSection: (id: string | null) => void;
  setDevice: (d: Device) => void;
  setLang: (lang: string) => void;
  setSave: (status: SaveStatus, error?: string | null) => void;
  markSaved: (savedDoc: SiteDocument, revision: number) => void;
}

function sectionExists(doc: SiteDocument, id: string | null) {
  return id !== null && doc.pages.some((p) => p.sections.some((s) => s.id === id));
}

function afterDocChange(state: EditorState, doc: SiteDocument) {
  const pageId = doc.pages.some((p) => p.id === state.pageId) ? state.pageId : (doc.pages[0]?.id ?? null);
  return {
    doc,
    pageId,
    selectedId: sectionExists(doc, state.selectedId) ? state.selectedId : null,
    // "conflict" is sticky: further edits must not hide it (the user has to reload)
    saveStatus:
      state.saveStatus === "conflict" || state.saveStatus === "saving"
        ? state.saveStatus
        : doc === state.savedDoc
          ? ("saved" as const)
          : ("dirty" as const),
  };
}

export const useEditor = create<EditorState>((set, get) => ({
  projectId: null,
  doc: null,
  savedDoc: null,
  revision: 0,
  saveStatus: "saved",
  saveError: null,
  undoStack: [],
  redoStack: [],
  pageId: null,
  lang: null,
  selectedId: null,
  device: "desktop",

  load: (projectId, doc, revision) =>
    set({
      projectId, doc, savedDoc: doc, revision, saveStatus: "saved", saveError: null,
      undoStack: [], redoStack: [],
      pageId: doc.pages[0]?.id ?? null,
      lang: doc.site.default_language,
      selectedId: null,
    }),

  apply: (recipe, opts) => {
    const state = get();
    if (!state.doc) return;
    const [next, patches, inverse] = produceWithPatches(state.doc, recipe);
    if (patches.length === 0) return;
    const now = Date.now();
    const stack = [...state.undoStack];
    const last = stack[stack.length - 1];
    if (opts?.coalesceKey && last?.key === opts.coalesceKey && now - last.at < COALESCE_MS) {
      // merge: replay both patch lists forwards; undo applies the newer inverse first
      stack[stack.length - 1] = {
        patches: [...last.patches, ...patches],
        inverse: [...inverse, ...last.inverse],
        key: opts.coalesceKey,
        at: now,
      };
    } else {
      stack.push({ patches, inverse, key: opts?.coalesceKey, at: now });
    }
    set({
      ...afterDocChange(state, next),
      undoStack: stack.slice(-MAX_HISTORY),
      redoStack: [],
    });
  },

  undo: () => {
    const state = get();
    const entry = state.undoStack[state.undoStack.length - 1];
    if (!entry || !state.doc) return;
    const doc = applyPatches(state.doc, entry.inverse);
    set({
      ...afterDocChange(state, doc),
      undoStack: state.undoStack.slice(0, -1),
      redoStack: [...state.redoStack, entry],
    });
  },

  redo: () => {
    const state = get();
    const entry = state.redoStack[state.redoStack.length - 1];
    if (!entry || !state.doc) return;
    const doc = applyPatches(state.doc, entry.patches);
    set({
      ...afterDocChange(state, doc),
      redoStack: state.redoStack.slice(0, -1),
      undoStack: [...state.undoStack, { ...entry, key: undefined }],
    });
  },

  selectPage: (pageId) => set({ pageId, selectedId: null }),
  selectSection: (selectedId) => set({ selectedId }),
  setDevice: (device) => set({ device }),
  setLang: (lang) => set({ lang }),
  setSave: (saveStatus, saveError = null) => set({ saveStatus, saveError }),
  markSaved: (savedDoc, revision) =>
    set((s) => ({
      savedDoc,
      revision,
      saveError: null,
      saveStatus: s.doc === savedDoc ? "saved" : "dirty",
    })),
}));

export function currentPage(state: Pick<EditorState, "doc" | "pageId">): Page | undefined {
  return state.doc?.pages.find((p) => p.id === state.pageId);
}
