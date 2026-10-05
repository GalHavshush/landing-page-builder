/** Helpers for reading the JSON Schema that Pydantic generates for section props. */
import type { PropSchema } from "@/api/types";
import { t } from "@/i18n";

export type Defs = Record<string, PropSchema>;

/**
 * Resolve $ref and Optional (anyOf [X, null]) wrappers into one flat schema.
 * Keys on the wrapper (control, title, group) win over the target's.
 */
export function unwrap(schema: PropSchema, defs: Defs): PropSchema {
  let result: PropSchema = { ...schema };
  const ref = result.$ref as string | undefined;
  if (ref) {
    const target = defs[ref.split("/").pop()!];
    delete result.$ref;
    result = { ...unwrap(target, defs), ...result };
  }
  const anyOf = result.anyOf as PropSchema[] | undefined;
  if (anyOf) {
    const inner = anyOf.find((s) => s.type !== "null");
    delete result.anyOf;
    if (inner) result = { ...unwrap(inner, defs), ...result };
  }
  return result;
}

export function isNullable(schema: PropSchema): boolean {
  return ((schema.anyOf as PropSchema[] | undefined) ?? []).some((s) => s.type === "null");
}

/** A starter value for a new repeater item, built from the item schema's defaults. */
export function blankItem(itemSchema: PropSchema, defs: Defs): Record<string, unknown> {
  const item = unwrap(itemSchema, defs);
  const out: Record<string, unknown> = {};
  for (const [name, prop] of Object.entries((item.properties ?? {}) as Record<string, PropSchema>)) {
    if ("default" in prop) out[name] = structuredClone(prop.default);
    else {
      const t = unwrap(prop, defs);
      out[name] = t.type === "string" ? (t.enum ? t.enum[0] : "") : t.type === "boolean" ? false : t.type === "array" ? [] : null;
    }
  }
  return out;
}

export function itemTitle(item: Record<string, unknown>, index: number): string {
  for (const key of ["title", "question", "label", "author", "name", "quote"]) {
    const v = item[key];
    if (typeof v === "string" && v.trim()) return v.slice(0, 40);
  }
  return t("Item {n}", { n: index + 1 });
}
