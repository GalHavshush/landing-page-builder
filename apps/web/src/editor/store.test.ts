import { beforeEach, describe, expect, it, vi } from "vitest";
import type { SiteDocument } from "@/api/types";
import * as c from "./commands";
import { useEditor } from "./store";

const sec = (id: string) =>
  ({ id, type: "text", variant: "single", style: {}, i18n: {}, props: { heading: id, body: "" } }) as never;
const base = () =>
  ({
    schema_version: 1,
    site: { name: "T", nav: [], default_language: "en", languages: ["en"] },
    theme: {},
    pages: [{ id: "p1", slug: "", title: "Home", seo: {}, i18n: {}, sections: [sec("a"), sec("b")] }],
  }) as unknown as SiteDocument;
const ids = () => useEditor.getState().doc!.pages[0].sections.map((s) => s.id);

beforeEach(() => {
  vi.useRealTimers();
  useEditor.getState().load(1, base(), 1);
});

describe("history", () => {
  it("undo and redo walk through edits", () => {
    const { apply, undo, redo } = useEditor.getState();
    apply(c.removeSection("a"));
    apply(c.addSection("p1", sec("z")));
    expect(ids()).toEqual(["b", "z"]);
    undo();
    expect(ids()).toEqual(["b"]);
    undo();
    expect(ids()).toEqual(["a", "b"]);
    redo();
    expect(ids()).toEqual(["b"]);
  });

  it("a new edit clears redo", () => {
    const { apply, undo } = useEditor.getState();
    apply(c.removeSection("a"));
    undo();
    apply(c.removeSection("b"));
    expect(useEditor.getState().redoStack).toHaveLength(0);
  });

  it("typing in one field is one undo step", () => {
    const { apply, undo } = useEditor.getState();
    for (const text of ["H", "He", "Hel", "Hell", "Hello"]) {
      useEditor.getState().apply(c.updateProps("a", { heading: text }), { coalesceKey: "a.heading" });
    }
    expect(useEditor.getState().undoStack).toHaveLength(1);
    undo();
    expect((useEditor.getState().doc!.pages[0].sections[0].props as { heading: string }).heading).toBe("a");
    void apply;
  });

  it("different fields do not merge", () => {
    const { apply } = useEditor.getState();
    apply(c.updateProps("a", { heading: "1" }), { coalesceKey: "a.heading" });
    apply(c.updateProps("a", { body: "2" }), { coalesceKey: "a.body" });
    expect(useEditor.getState().undoStack).toHaveLength(2);
  });

  it("a no-op edit records nothing", () => {
    useEditor.getState().apply(() => {});
    expect(useEditor.getState().undoStack).toHaveLength(0);
  });

  it("clears the selection when the selected section disappears", () => {
    const s = useEditor.getState();
    s.selectSection("a");
    s.apply(c.removeSection("a"));
    expect(useEditor.getState().selectedId).toBeNull();
  });

  it("marks the document dirty after an edit", () => {
    useEditor.getState().apply(c.removeSection("a"));
    expect(useEditor.getState().saveStatus).toBe("dirty");
  });
});
