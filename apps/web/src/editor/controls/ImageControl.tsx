import { FieldShell, type ControlProps } from "./basic";

export interface ImageValue {
  asset: string;
  alt: string;
}

/** Placeholder until uploads exist (M15). Keeps the existing value untouched. */
export function ImageControl({ label, value }: ControlProps<ImageValue | null>) {
  return (
    <FieldShell label={label}>
      <p className="mt-1 rounded bg-slate-50 px-2 py-1.5 text-xs text-slate-500">
        {value ? `Image ${value.asset}` : "No image"} · uploads arrive in the next step.
      </p>
    </FieldShell>
  );
}
