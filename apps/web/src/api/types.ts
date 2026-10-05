/** Short names for the generated API types (see `npm run gen`). */
import type { components } from "./generated/api";

export type User = components["schemas"]["UserOut"];
export type Project = components["schemas"]["ProjectOut"];
export type { SiteDocument } from "./generated/document";
