import { useEffect } from "react";
import { api } from "@/api/client";
import { Autosaver } from "./autosave";
import { useEditor } from "./store";

/** The running autosaver, so other UI (Export) can flush pending edits first. */
export const saver: { current: Autosaver | null } = { current: null };

export function useAutosave(projectId: number) {
  useEffect(() => {
    const autosaver = new Autosaver((doc, base_revision) =>
      api<{ revision: number }>(`/projects/${projectId}/doc`, { method: "PUT", body: { doc, base_revision } }),
    );
    saver.current = autosaver;
    autosaver.start();
    const warn = (e: BeforeUnloadEvent) => {
      const { doc, savedDoc } = useEditor.getState();
      if (doc !== savedDoc) e.preventDefault(); // browser shows its "unsaved changes" prompt
    };
    window.addEventListener("beforeunload", warn);
    return () => {
      autosaver.stop();
      saver.current = null;
      window.removeEventListener("beforeunload", warn);
    };
  }, [projectId]);
}

/** Ctrl/Cmd+Z, Shift+Ctrl/Cmd+Z, Ctrl+Y, Ctrl/Cmd+S. Inside text inputs the browser's own undo wins. */
export function useShortcuts() {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      if (!mod) return;
      const key = e.key.toLowerCase();
      if (key === "s") {
        e.preventDefault();
        void saver.current?.flush();
        return;
      }
      const el = e.target as HTMLElement;
      if (el.closest("input, textarea, select, [contenteditable=true]")) return;
      const { undo, redo } = useEditor.getState();
      if (key === "z" && !e.shiftKey) (e.preventDefault(), undo());
      else if ((key === "z" && e.shiftKey) || key === "y") (e.preventDefault(), redo());
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
