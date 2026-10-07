import { useEffect, useId, useState } from "react";
import { FieldShell, type ControlProps } from "./basic";

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/** URL slug field: committed only when valid and not used by another page. */
export function SlugControl({
  label, value, onChange, taken, disabled, placeholder,
}: ControlProps<string> & { taken: string[] }) {
  const id = useId();
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  const problem = draft === "" ? "A page needs a URL name" : !SLUG.test(draft) ? "Use lowercase letters, numbers and single hyphens" : taken.includes(draft) ? "Another page already uses this" : null;
  return (
    <FieldShell label={label} htmlFor={id}>
      <div className="mt-1 flex items-center rounded-md border border-ink-300 bg-white text-sm focus-within:border-ink-900">
        <span className="pl-2.5 text-ink-400">/</span>
        <input id={id} value={draft} disabled={disabled} placeholder={placeholder} aria-invalid={Boolean(problem)} spellCheck={false}
          onBlur={() => setDraft(value)} // leaving the field with something unusable puts the saved name back
          onChange={(e) => {
            const v = e.target.value.toLowerCase();
            setDraft(v);
            if (v !== "" && SLUG.test(v) && !taken.includes(v)) onChange(v, true);
          }}
          className="w-full rounded-md bg-transparent px-1 py-1.5 focus:outline-none disabled:text-ink-400" />
      </div>
      {!disabled && problem && <p className="mt-1 text-xs text-red-600">{problem}</p>}
      {disabled && <p className="mt-1 text-xs text-ink-400">The home page always lives at the site root.</p>}
    </FieldShell>
  );
}
