import type { ButtonHTMLAttributes, InputHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "danger" | "quiet";

const BASE =
  "inline-flex select-none items-center justify-center gap-1.5 whitespace-nowrap rounded-md text-[13px] font-medium transition duration-150 active:translate-y-px disabled:pointer-events-none disabled:opacity-40";
const VARIANTS: Record<Variant, string> = {
  primary: "bg-ink-900 text-white hover:bg-ink-700 shadow-[inset_0_1px_0_rgb(255_255_255/0.12)]",
  ghost: "border border-ink-300 bg-white text-ink-800 hover:border-ink-400 hover:bg-ink-50",
  quiet: "text-ink-600 hover:bg-ink-100 hover:text-ink-900",
  danger: "border border-red-600/30 bg-white text-red-600 hover:bg-red-600 hover:text-white",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return <button {...props} className={`${BASE} h-8 px-3 ${VARIANTS[variant]} ${className}`} />;
}

export const linkButton = `${BASE} h-8 px-3 ${VARIANTS.primary}`;

export function Field({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block">
      <span className="field-label">{label}</span>
      <input {...props} className="field-input mt-1" />
    </label>
  );
}

export function ErrorText({ children }: { children?: React.ReactNode }) {
  return children ? (
    <p role="alert" className="text-[13px] text-red-600">
      {children}
    </p>
  ) : null;
}
