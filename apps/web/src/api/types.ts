/** Short names for the generated API types (see `npm run gen`). */
import type { components } from "./generated/api";
import type { SiteDocument } from "./generated/document";

export type User = components["schemas"]["UserOut"];
export type Project = components["schemas"]["ProjectOut"];
export type Asset = components["schemas"]["AssetOut"];
export type PostOut = components["schemas"]["PostOut"];
export type PostIn = components["schemas"]["PostIn"];
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
  description: string;
  variants: string[];
  template: Section;
  props_schema: { properties: Record<string, PropSchema>; $defs?: Record<string, unknown> };
}

export interface EditorMeta {
  sections: SectionMeta[];
  icons: string[];
  fonts: FontOption[];
  radii: string[];
  section_style_schema: { properties: Record<string, PropSchema> };
  theme_schema: unknown;
  languages: Record<string, string>;
  rtl_languages: string[];
  starters: string[];
  starter_info: { id: string; label: string; description: string; theme: SiteDocument["theme"] }[];
}

export interface FontOption {
  key: string;
  label: string;
  kind: "system" | "sans" | "serif";
  scripts: string[]; // scripts beyond Latin the font can draw, e.g. ["hebrew"]
  file: string | null; // Latin file under /fonts/, used for the sample line
}
