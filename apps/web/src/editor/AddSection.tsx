import { useRef } from "react";
import type { EditorMeta, SectionMeta } from "@/api/types";
import { IconClose, IconPlus, SectionIcon } from "@/components/icons";
import { addSection, newId } from "./commands";
import { currentPage, useEditor } from "./store";
import { t } from "@/i18n";

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
      <button onClick={() => dialog.current?.showModal()}
        className="flex w-full items-center gap-2 rounded-md border border-dashed border-ink-300 px-2.5 py-2 text-[13px] text-ink-600 transition hover:border-ink-900 hover:bg-white hover:text-ink-900">
        <IconPlus size={14} /> {t("Add section")}
      </button>
      <dialog
        ref={dialog}
        className="m-auto w-[min(44rem,94vw)] rounded-2xl bg-white p-0"
        onClick={(e) => e.target === dialog.current && dialog.current?.close()}
      >
        <div className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-[15px] font-semibold tracking-tight">{t("Add a section")}</h2>
              <p className="text-[13px] text-ink-500">{t("Goes after the section you have selected.")}</p>
            </div>
            <button aria-label={t("Close")} className="grid h-7 w-7 place-items-center rounded-md text-ink-500 hover:bg-ink-100 hover:text-ink-900" onClick={() => dialog.current?.close()}>
              <IconClose size={15} />
            </button>
          </div>
          <ul className="grid gap-2 sm:grid-cols-2">
            {meta.sections.map((m) => (
              <li key={m.type}>
                <button
                  onClick={() => add(m)}
                  className="group flex h-full w-full items-start gap-3 rounded-lg border border-ink-200 p-3 text-start transition hover:border-ink-900 hover:bg-ink-50"
                >
                  <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-md bg-ink-100 text-ink-700 transition group-hover:bg-ink-900 group-hover:text-white">
                    <SectionIcon type={m.type} size={16} />
                  </span>
                  <span>
                    <span className="block text-[13px] font-medium">{t(m.label)}</span>
                    <span className="mt-0.5 block text-[12px] leading-snug text-ink-500">{t(m.description)}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </dialog>
    </>
  );
}
