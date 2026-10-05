import { useRef } from "react";
import type { Asset } from "@/api/types";
import { AssetPicker } from "../controls/ImageControl";
import { insertAt, makeLink, prefixLines, wrap, type Edit } from "../markdown";
import { useEditor } from "../store";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

/** A Markdown textarea with a formatting toolbar. The live preview next to it is the real page. */
export function MarkdownEditor({ value, onChange }: Props) {
  const area = useRef<HTMLTextAreaElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const projectId = useEditor((s) => s.projectId)!;

  const run = (fn: (text: string, start: number, end: number) => Edit) => {
    const el = area.current!;
    const edit = fn(el.value, el.selectionStart, el.selectionEnd);
    onChange(edit.text);
    requestAnimationFrame(() => {
      el.focus();
      el.setSelectionRange(edit.start, edit.end);
    });
  };
  const insertImage = (a: Asset) => {
    run((t, s) => insertAt(t, s, `![${a.alt_default || a.filename}](asset:${a.id})`));
    dialog.current?.close();
  };

  const btn = "rounded px-2 py-1 text-[12px] font-medium text-ink-600 transition hover:bg-ink-100 hover:text-ink-900";
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div role="toolbar" aria-label="Formatting" className="flex flex-wrap items-center gap-0.5 border-b border-ink-200 bg-white px-2 py-1">
        <button className={`${btn} font-bold`} title="Bold" aria-label="Bold" onClick={() => run((t, s, e) => wrap(t, s, e, "**"))}>B</button>
        <button className={`${btn} italic`} title="Italic" aria-label="Italic" onClick={() => run((t, s, e) => wrap(t, s, e, "*"))}>I</button>
        <span className="mx-1 h-4 w-px bg-ink-200" />
        <button className={btn} title="Heading" aria-label="Heading" onClick={() => run((t, s, e) => prefixLines(t, s, e, "## "))}>H2</button>
        <button className={btn} title="Subheading" aria-label="Subheading" onClick={() => run((t, s, e) => prefixLines(t, s, e, "### "))}>H3</button>
        <span className="mx-1 h-4 w-px bg-ink-200" />
        <button className={btn} title="Bulleted list" aria-label="Bulleted list" onClick={() => run((t, s, e) => prefixLines(t, s, e, "- "))}>Bullets</button>
        <button className={btn} title="Numbered list" aria-label="Numbered list" onClick={() => run((t, s, e) => prefixLines(t, s, e, (i) => `${i + 1}. `))}>Numbered</button>
        <button className={btn} title="Quote" aria-label="Quote" onClick={() => run((t, s, e) => prefixLines(t, s, e, "> "))}>Quote</button>
        <span className="mx-1 h-4 w-px bg-ink-200" />
        <button className={btn} title="Link" aria-label="Link" onClick={() => run((t, s, e) => makeLink(t, s, e))}>Link</button>
        <button className={btn} title="Insert image" aria-label="Insert image" onClick={() => dialog.current?.showModal()}>Image</button>
      </div>
      <textarea
        ref={area}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Post text"
        spellCheck
        placeholder="Write your post here. Use the toolbar for headings, lists, links and images."
        className="min-h-0 flex-1 resize-none bg-white p-4 font-mono text-[13px] leading-[1.7] focus:outline-none"
      />
      <AssetPicker dialogRef={dialog} projectId={projectId} onPick={insertImage} />
    </div>
  );
}
