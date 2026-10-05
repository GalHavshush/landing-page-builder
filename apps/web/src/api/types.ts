/** Short names for the generated API types (see `npm run gen`). */
import type { components } from "./generated/api";
import type { SiteDocument } from "./generated/document";

export type User = components["schemas"]["UserOut"];
export type Project = components["schemas"]["ProjectOut"];
export type { SiteDocument };
export type Page = SiteDocument["pages"][number];
export type Section = Page["sections"][number];

/** JSON Schema property carrying the editor hints added in sitegen.models.field(). */
export interface PropSchema {
  type?: string;
  title?: string;
  group?: "content" | "design";
  control?: string;
  enum?: (string | number)[];
  default?: unknown;
  [key: string]: unknown;
}

export interface SectionMeta {
  type: string;
  label: string;
  variants: string[];
  template: Section;
  props_schema: { properties: Record<string, PropSchema>; $defs?: Record<string, unknown> };
}

export interface EditorMeta {
  sections: SectionMeta[];
  icons: string[];
  fonts: string[];
  radii: string[];
  languages: Record<string, string>;
  rtl_languages: string[];
  starters: string[];
}
