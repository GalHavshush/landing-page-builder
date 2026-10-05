import { useId } from "react";
import { t } from "@/i18n";

export interface ControlProps<T = unknown> {
  label: string;
  value: T;
  /** `typing` = a keystroke-level change (merged into one undo step) */
  onChange: (value: T, typing?: boolean) => void;
  placeholder?: string;
  disabled?: boolean;
  hint?: string;
}

export function FieldShell({ label, hint, htmlFor, children }: { label: string; hint?: string; htmlFor?: string; children: React.ReactNode }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="field-label">
        {t(label)}
      </label>
      <div className="mt-1">{children}</div>
      {hint && <p className="mt-1.5 text-[12px] leading-snug text-ink-500">{t(hint)}</p>}
    </div>
  );
}

export function TextControl({ label, value, onChange, placeholder, disabled, hint }: ControlProps<string>) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <input id={id} dir="auto" className="field-input" value={value} placeholder={placeholder} disabled={disabled}
        onChange={(e) => onChange(e.target.value, true)} />
    </FieldShell>
  );
}

export function TextAreaControl({ label, value, onChange, placeholder, disabled, hint, rows = 3 }: ControlProps<string> & { rows?: number }) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <textarea id={id} dir="auto" rows={rows} className="field-input resize-y" value={value} placeholder={placeholder} disabled={disabled}
        onChange={(e) => onChange(e.target.value, true)} />
    </FieldShell>
  );
}

/** Options in a recessed track; the chosen one sits raised, like a physical switch. */
export function SegmentedControl<T extends string | number>({
  label, value, onChange, options, disabled,
}: ControlProps<T> & { options: { value: T; label: string }[] }) {
  return (
    <FieldShell label={label}>
      <div role="group" aria-label={t(label)} className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200">
        {options.map((o) => {
          const on = o.value === value;
          return (
            <button
              key={String(o.value)}
              type="button"
              disabled={disabled}
              aria-pressed={on}
              onClick={() => onChange(o.value)}
              className={`flex-1 rounded-[5px] px-2 py-[5px] text-[12px] font-medium capitalize transition duration-150 disabled:opacity-50 ${
                on ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-600 hover:text-ink-900"
              }`}
            >
              {t(o.label)}
            </button>
          );
        })}
      </div>
    </FieldShell>
  );
}

export function SelectControl<T extends string | number>({
  label, value, onChange, options, disabled,
}: ControlProps<T> & { options: { value: T; label: string }[] }) {
  const id = useId();
  return (
    <FieldShell label={label} htmlFor={id}>
      <select id={id} className="field-input appearance-none bg-[length:12px] bg-[right_10px_center] bg-no-repeat pe-8 rtl:bg-[left_10px_center]"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%237d796e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E")` }}
        value={String(value)} disabled={disabled}
        onChange={(e) => onChange(options.find((o) => String(o.value) === e.target.value)!.value)}>
        {options.map((o) => (
          <option key={String(o.value)} value={String(o.value)}>{t(o.label)}</option>
        ))}
      </select>
    </FieldShell>
  );
}

export function ToggleControl({ label, value, onChange, disabled }: ControlProps<boolean>) {
  const id = useId();
  return (
    <div className="flex items-center justify-between gap-3">
      <label htmlFor={id} className="text-[13px] text-ink-800">{t(label)}</label>
      <button
        id={id} type="button" role="switch" aria-checked={value} disabled={disabled} onClick={() => onChange(!value)}
        className={`relative h-[18px] w-[30px] shrink-0 rounded-full transition-colors duration-150 disabled:opacity-40 ${value ? "bg-ink-900" : "bg-ink-300"}`}
      >
        <span className={`absolute start-[2px] top-[2px] h-[14px] w-[14px] rounded-full bg-[#fff] shadow-sm transition-transform duration-150 ${value ? "translate-x-3 rtl:-translate-x-3" : ""}`} />
      </button>
    </div>
  );
}
