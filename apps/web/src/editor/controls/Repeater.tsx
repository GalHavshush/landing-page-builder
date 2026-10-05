import { useState } from "react";
import { IconChevronRight, IconClose } from "@/components/icons";
import { itemTitle } from "./schema";

/**
 * A list of items edited inline: expand to edit, move up/down, remove, add.
 * `renderItem` draws the fields of one item (the registry supplies it from the item schema).
 */
export function Repeater<T extends object>({
  label, items, onChange, renderItem, makeBlank, addLabel,
}: {
  label: string;
  items: T[];
  onChange: (items: T[], typing?: boolean) => void;
  renderItem: (item: T, set: (next: T, typing?: boolean) => void, index: number) => React.ReactNode;
  makeBlank: () => T;
  addLabel: string;
}) {
  const [open, setOpen] = useState<number | null>(items.length === 1 ? 0 : null);

  const move = (i: number, d: -1 | 1) => {
    const next = [...items];
    [next[i], next[i + d]] = [next[i + d], next[i]];
    setOpen(open === i ? i + d : open === i + d ? i : open);
    onChange(next);
  };
  const remove = (i: number) => {
    onChange(items.filter((_, j) => j !== i));
    setOpen(null);
  };

  return (
    <div>
      <div className="field-label">{label}</div>
      <ul className="mt-1 space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="rounded-md border border-ink-200 bg-white">
            <div className="flex items-center">
              <button type="button" aria-expanded={open === i} onClick={() => setOpen(open === i ? null : i)}
                className="flex min-w-0 flex-1 items-center truncate px-2 py-2 text-left text-[13px] font-medium">
                <IconChevronRight size={13} className={`mr-1 shrink-0 text-ink-400 transition-transform duration-150 ${open === i ? "rotate-90" : ""}`} />
                {itemTitle(item as Record<string, unknown>, i)}
              </button>
              <div className="flex gap-0.5 pr-1 text-ink-500">
                <button type="button" aria-label={`Move ${itemTitle(item as Record<string, unknown>, i)} up`} disabled={i === 0} onClick={() => move(i, -1)}
                  className="grid h-6 w-6 place-items-center rounded hover:bg-ink-200 disabled:opacity-25"><IconChevronRight size={13} className="-rotate-90" /></button>
                <button type="button" aria-label={`Move ${itemTitle(item as Record<string, unknown>, i)} down`} disabled={i === items.length - 1} onClick={() => move(i, 1)}
                  className="grid h-6 w-6 place-items-center rounded hover:bg-ink-200 disabled:opacity-25"><IconChevronRight size={13} className="rotate-90" /></button>
                <button type="button" aria-label={`Remove ${itemTitle(item as Record<string, unknown>, i)}`} onClick={() => remove(i)}
                  className="grid h-6 w-6 place-items-center rounded hover:bg-red-600 hover:text-white"><IconClose size={13} /></button>
              </div>
            </div>
            {open === i && (
              <div className="space-y-3 border-t border-ink-200 bg-ink-50/60 p-3">
                {renderItem(item, (next, typing) => onChange(items.map((x, j) => (j === i ? next : x)), typing), i)}
              </div>
            )}
          </li>
        ))}
      </ul>
      <button type="button" onClick={() => { onChange([...items, makeBlank()]); setOpen(items.length); }}
        className="mt-2 flex w-full items-center justify-center gap-1.5 rounded-md border border-dashed border-ink-300 py-1.5 text-[13px] text-ink-600 transition hover:border-ink-900 hover:text-ink-900">
        + {addLabel}
      </button>
    </div>
  );
}
