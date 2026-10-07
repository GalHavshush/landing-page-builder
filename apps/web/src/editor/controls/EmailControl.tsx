import { useEffect, useId, useState } from "react";
import { t } from "@/i18n";
import { isEmail } from "../validation";
import { FieldShell, type ControlProps } from "./basic";

/** Email field: only an empty or well-formed address is saved; anything else shows what is wrong. */
export function EmailControl({ label, value, onChange }: ControlProps<string>) {
  const id = useId();
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  const bad = draft.trim() !== "" && !isEmail(draft);
  return (
    <FieldShell label={label} htmlFor={id}>
      <input id={id} dir="ltr" type="text" inputMode="email" autoComplete="off" spellCheck={false} value={draft} aria-invalid={bad}
        aria-describedby={bad ? `${id}-err` : undefined}
        onChange={(e) => {
          setDraft(e.target.value);
          if (e.target.value.trim() === "" || isEmail(e.target.value)) onChange(e.target.value.trim(), true);
        }}
        className={`field-input ${bad ? "!border-red-400" : ""}`} />
      {bad && <p id={`${id}-err`} role="alert" className="mt-1 text-xs text-red-600">{t("Enter an email like name@example.com. It is not saved until it looks right.")}</p>}
    </FieldShell>
  );
}
