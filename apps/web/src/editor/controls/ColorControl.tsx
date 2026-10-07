import { useEffect, useId, useState } from "react";
import { isHex } from "../contrast";
import { FieldShell, type ControlProps } from "./basic";

/** Color picker + hex field. Only valid #RRGGBB values are committed. */
export function ColorControl({ label, value, onChange }: ControlProps<string>) {
  const id = useId();
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  const invalid = !isHex(draft);
  return (
    <FieldShell label={label} htmlFor={id}>
      <div className="mt-1 flex items-center gap-2">
        <input type="color" aria-label={`${label} picker`} value={isHex(value) ? value.toLowerCase() : "#000000"}
          onChange={(e) => onChange(e.target.value.toUpperCase(), true)}
          className="h-8 w-10 cursor-pointer rounded border border-ink-300 bg-white p-0.5" />
        <input id={id} value={draft} aria-invalid={invalid} spellCheck={false}
          onChange={(e) => {
            setDraft(e.target.value);
            if (isHex(e.target.value)) onChange(e.target.value.toUpperCase(), true);
          }}
          className={`w-28 rounded-md border px-2 py-1.5 font-mono text-sm ${invalid ? "border-red-400" : "border-ink-300"}`} />
      </div>
      {invalid && <p role="alert" className="mt-1 text-xs text-red-600">Use a colour like #2563EB. It is not applied until it looks right.</p>}
    </FieldShell>
  );
}
