import { useEffect, useId, useState } from "react";
import { FieldShell, type ControlProps } from "./basic";

export interface LinkValue {
  page?: string | null;
  url?: string | null;
  asset?: string | null;
}

type Kind = "page" | "web" | "email" | "phone";

// Same rule as the server (sitegen.models.Link): only safe schemes are accepted.
const SAFE_URL = /^(https?:\/\/|mailto:|tel:|#)/i;

function kindOf(v: LinkValue | null): Kind {
  if (v?.page != null) return "page";
  const url = v?.url ?? "";
  if (/^mailto:/i.test(url)) return "email";
  if (/^tel:/i.test(url)) return "phone";
  return "web";
}

const PREFIX: Record<Exclude<Kind, "page">, string> = { web: "https://", email: "mailto:", phone: "tel:" };

/**
 * Link target picker: a page of this site, a web address, an email or a phone number.
 * Partially typed URLs are kept locally and only committed once valid, so an incomplete
 * link can never be autosaved (the server would reject it).
 */
export function LinkControl({
  label, value, onChange, pages, optional,
}: ControlProps<LinkValue | null> & { pages: { id: string; title: string }[]; optional?: boolean }) {
  const id = useId();
  const kind = kindOf(value);
  const [draft, setDraft] = useState(value?.url ?? "");
  useEffect(() => setDraft(value?.url ?? ""), [value?.url]);
  const invalid = kind !== "page" && draft !== "" && !SAFE_URL.test(draft);

  const setKind = (k: Kind) => {
    if (k === "page") onChange({ page: pages[0]?.id ?? "" });
    else onChange({ url: PREFIX[k] });
  };

  return (
    <FieldShell label={label}>
      <div className="mt-1 space-y-1.5">
        <select aria-label={`${label} type`} className="block w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"
          value={value ? kind : "none"}
          onChange={(e) => (e.target.value === "none" ? onChange(null) : setKind(e.target.value as Kind))}>
          {optional && <option value="none">No link</option>}
          <option value="page">Page on this site</option>
          <option value="web">Web address</option>
          <option value="email">Email address</option>
          <option value="phone">Phone number</option>
        </select>
        {value && kind === "page" && (
          <select aria-label={`${label} page`} className="block w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"
            value={value.page ?? ""} onChange={(e) => onChange({ page: e.target.value })}>
            {pages.map((p) => (
              <option key={p.id} value={p.id}>{p.title}</option>
            ))}
          </select>
        )}
        {value && kind !== "page" && (
          <>
            <input id={id} aria-label={`${label} address`} aria-invalid={invalid} value={draft}
              className={`block w-full rounded-md border px-2.5 py-1.5 text-sm ${invalid ? "border-red-400" : "border-slate-300"}`}
              onChange={(e) => {
                setDraft(e.target.value);
                if (SAFE_URL.test(e.target.value)) onChange({ url: e.target.value }, true);
              }} />
            {invalid && <p className="text-xs text-red-600">Must start with https://, mailto: or tel:</p>}
          </>
        )}
      </div>
    </FieldShell>
  );
}
