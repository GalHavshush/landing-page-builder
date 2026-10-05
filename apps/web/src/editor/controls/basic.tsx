import { useId } from "react";

export interface ControlProps<T = unknown> {
  label: string;
  value: T;
  /** `typing` = a keystroke-level change (merged into one undo step) */
  onChange: (value: T, typing?: boolean) => void;
  placeholder?: string;
  disabled?: boolean;
  hint?: string;
}

const inputCls =
  "mt-1 block w-full rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100 disabled:text-slate-400";

export function FieldShell({ label, hint, htmlFor, children }: { label: string; hint?: string; htmlFor?: string; children: React.ReactNode }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block text-xs font-medium text-slate-600">
        {label}
      </label>
      {children}
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  );
}

export function TextControl({ label, value, onChange, placeholder, disabled, hint }: ControlProps<string>) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <input id={id} className={inputCls} value={value} placeholder={placeholder} disabled={disabled}
        onChange={(e) => onChange(e.target.value, true)} />
    </FieldShell>
  );
}

export function TextAreaControl({ label, value, onChange, placeholder, disabled, hint, rows = 3 }: ControlProps<string> & { rows?: number }) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <textarea id={id} rows={rows} className={inputCls} value={value} placeholder={placeholder} disabled={disabled}
        onChange={(e) => onChange(e.target.value, true)} />
    </FieldShell>
  );
}

export function SegmentedControl<T extends string | number>({
  label, value, onChange, options, disabled,
}: ControlProps<T> & { options: { value: T; label: string }[] }) {
  return (
    <FieldShell label={label}>
      <div role="group" aria-label={label} className="mt-1 flex overflow-hidden rounded-md border border-slate-300 text-sm">
        {options.map((o) => (
          <button
            key={String(o.value)}
            type="button"
            disabled={disabled}
            aria-pressed={o.value === value}
            onClick={() => onChange(o.value)}
            className={`flex-1 px-2 py-1.5 capitalize transition disabled:opacity-50 ${
              o.value === value ? "bg-indigo-600 text-white" : "bg-white text-slate-600 hover:bg-slate-50"
            }`}
          >
            {o.label}
          </button>
        ))}
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
      <select id={id} className={inputCls} value={String(value)} disabled={disabled}
        onChange={(e) => onChange(options.find((o) => String(o.value) === e.target.value)!.value)}>
        {options.map((o) => (
          <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
        ))}
      </select>
    </FieldShell>
  );
}

export function ToggleControl({ label, value, onChange, disabled }: ControlProps<boolean>) {
  const id = useId();
  return (
    <div className="flex items-center justify-between">
      <label htmlFor={id} className="text-sm text-slate-700">{label}</label>
      <input id={id} type="checkbox" checked={value} disabled={disabled} onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
    </div>
  );
}
