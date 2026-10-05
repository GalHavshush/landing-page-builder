import type { EditorMeta, PropSchema } from "@/api/types";
import { SegmentedControl, SelectControl, TextAreaControl, TextControl, ToggleControl } from "./basic";
import { ImageControl, type ImageValue } from "./ImageControl";
import { LinkControl, type LinkValue } from "./LinkControl";
import { Repeater } from "./Repeater";
import { blankItem, isNullable, unwrap, type Defs } from "./schema";

const humanize = (s: string) => s.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

/** What controls need to know about the surrounding document and schema. */
export interface Env {
  meta: EditorMeta;
  pages: { id: string; title: string }[];
  defs: Defs;
}

interface Props {
  name: string;
  schema: PropSchema;
  value: unknown;
  onChange: (value: unknown, typing?: boolean) => void;
  env: Env;
  placeholder?: string;
  hint?: string;
  label?: string;
}

/** Picks the editing control for a schema node from its `control` hint (or its JSON type). */
export function Control({ name, schema, value, onChange, env, placeholder, hint, label }: Props) {
  const resolved = unwrap(schema, env.defs);
  const control = (schema.control as string | undefined) ?? (resolved.control as string | undefined);
  const text = label ?? (schema.title as string | undefined) ?? humanize(name);

  switch (control) {
    case "text":
      return <TextControl label={text} value={(value as string) ?? ""} onChange={onChange} placeholder={placeholder} hint={hint} />;
    case "textarea":
    case "richtext":
      return (
        <TextAreaControl label={text} value={(value as string) ?? ""} onChange={onChange} placeholder={placeholder}
          rows={control === "richtext" ? 6 : 3}
          hint={hint ?? (control === "richtext" ? "Supports Markdown: **bold**, *italic*, lists, [links](https://…)" : undefined)} />
      );
    case "segmented":
    case "select": {
      const options = (resolved.enum ?? []).map((v) => ({ value: v, label: String(v) }));
      const Cmp = control === "segmented" && options.length <= 4 ? SegmentedControl : SelectControl;
      return <Cmp label={text} value={value as string | number} options={options} onChange={(v) => onChange(v)} />;
    }
    case "toggle":
      return <ToggleControl label={text} value={Boolean(value)} onChange={(v) => onChange(v)} />;
    case "icon":
      return (
        <SelectControl label={text} value={(value as string | null) ?? ""}
          options={[{ value: "", label: "No icon" }, ...env.meta.icons.map((i) => ({ value: i, label: i }))]}
          onChange={(v) => onChange(v === "" ? null : v)} />
      );
    case "link":
      return <LinkControl label={text} value={(value as LinkValue | null) ?? null} pages={env.pages}
        optional={isNullable(schema)} onChange={onChange as (v: LinkValue | null) => void} />;
    case "image":
      return <ImageControl label={text} value={(value as ImageValue | null) ?? null} onChange={onChange as (v: ImageValue | null) => void} />;
    case "repeater":
    case "buttons": {
      const itemSchema = (resolved.items ?? {}) as PropSchema;
      const item = unwrap(itemSchema, env.defs);
      const fields = Object.entries((item.properties ?? {}) as Record<string, PropSchema>);
      const noun = control === "buttons" ? "button" : "item";
      return (
        <Repeater
          label={text}
          items={(value as Record<string, unknown>[]) ?? []}
          onChange={onChange as (v: Record<string, unknown>[], typing?: boolean) => void}
          makeBlank={() => (control === "buttons" ? { ...blankItem(itemSchema, env.defs), label: "Button", href: { url: "https://" } } : blankItem(itemSchema, env.defs))}
          addLabel={`Add ${noun}`}
          renderItem={(it, set) =>
            fields.map(([field, fieldSchema]) => (
              <Control key={field} name={field} schema={fieldSchema} env={env} value={it[field]}
                onChange={(v, typing) => set({ ...it, [field]: v }, typing)} />
            ))
          }
        />
      );
    }
  }
  // no hint: fall back on the JSON type
  if (resolved.type === "boolean") return <ToggleControl label={text} value={Boolean(value)} onChange={(v) => onChange(v)} />;
  if (resolved.type === "string") return <TextControl label={text} value={(value as string) ?? ""} onChange={onChange} />;
  return <p className="rounded bg-ink-50 px-2 py-1.5 text-xs text-ink-500">{text}: no editor for this field yet.</p>;
}
