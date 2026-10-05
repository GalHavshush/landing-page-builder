import { useState } from "react";
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
      <div className="text-xs font-medium text-slate-600">{label}</div>
      <ul className="mt-1 space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="rounded-md border border-slate-200 bg-slate-50/60">
            <div className="flex items-center">
              <button type="button" aria-expanded={open === i} onClick={() => setOpen(open === i ? null : i)}
                className="min-w-0 flex-1 truncate px-2.5 py-2 text-left text-sm font-medium">
                <span className="mr-1.5 text-slate-400">{open === i ? "▾" : "▸"}</span>
                {itemTitle(item as Record<string, unknown>, i)}
              </button>
              <div className="flex gap-0.5 pr-1 text-slate-500">
                <button type="button" aria-label={`Move ${itemTitle(item as Record<string, unknown>, i)} up`} disabled={i === 0} onClick={() => move(i, -1)}
                  className="rounded px-1.5 py-1 hover:bg-slate-200 disabled:opacity-25">↑</button>
                <button type="button" aria-label={`Move ${itemTitle(item as Record<string, unknown>, i)} down`} disabled={i === items.length - 1} onClick={() => move(i, 1)}
                  className="rounded px-1.5 py-1 hover:bg-slate-200 disabled:opacity-25">↓</button>
                <button type="button" aria-label={`Remove ${itemTitle(item as Record<string, unknown>, i)}`} onClick={() => remove(i)}
                  className="rounded px-1.5 py-1 hover:bg-red-50 hover:text-red-600">✕</button>
              </div>
            </div>
            {open === i && (
              <div className="space-y-3 border-t border-slate-200 p-2.5">
                {renderItem(item, (next, typing) => onChange(items.map((x, j) => (j === i ? next : x)), typing), i)}
              </div>
            )}
          </li>
        ))}
      </ul>
      <button type="button" onClick={() => { onChange([...items, makeBlank()]); setOpen(items.length); }}
        className="mt-2 w-full rounded-md border border-dashed border-slate-300 py-1.5 text-sm text-slate-600 hover:border-indigo-400 hover:text-indigo-700">
        + {addLabel}
      </button>
    </div>
  );
}
