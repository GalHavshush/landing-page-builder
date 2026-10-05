import { useRef } from "react";
import type { EditorMeta, SectionMeta } from "@/api/types";
import { Button } from "@/components/ui";
import { addSection, newId } from "./commands";
import { currentPage, useEditor } from "./store";

/** "Add section" button + a native <dialog> (focus trap and Esc come for free). */
export function AddSection({ meta }: { meta: EditorMeta }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const apply = useEditor((s) => s.apply);
  const selectSection = useEditor((s) => s.selectSection);

  const add = (m: SectionMeta) => {
    const state = useEditor.getState();
    const page = currentPage(state);
    if (!page) return;
    const at = state.selectedId ? page.sections.findIndex((s) => s.id === state.selectedId) + 1 : page.sections.length;
    const section = { ...structuredClone(m.template), id: newId("sec") };
    apply(addSection(page.id, section, at));
    selectSection(section.id);
    dialog.current?.close();
  };

  return (
    <>
      <Button variant="ghost" className="w-full" onClick={() => dialog.current?.showModal()}>
        + Add section
      </Button>
      <dialog
        ref={dialog}
        className="m-auto w-[min(40rem,92vw)] rounded-xl p-0 shadow-2xl backdrop:bg-slate-900/40"
        onClick={(e) => e.target === dialog.current && dialog.current?.close()}
      >
        <div className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Add a section</h2>
            <button aria-label="Close" className="text-slate-500 hover:text-slate-900" onClick={() => dialog.current?.close()}>
              ✕
            </button>
          </div>
          <ul className="grid gap-3 sm:grid-cols-2">
            {meta.sections.map((m) => (
              <li key={m.type}>
                <button
                  onClick={() => add(m)}
                  className="h-full w-full rounded-lg border border-slate-200 p-3 text-left transition hover:border-indigo-400 hover:bg-indigo-50"
                >
                  <div className="font-medium">{m.label}</div>
                  <div className="mt-0.5 text-xs text-slate-500">{m.description}</div>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </dialog>
    </>
  );
}
