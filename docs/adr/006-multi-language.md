# ADR 006: Multi-language from day one

Status: accepted

## Context
First clients need multi-language sites (possibly RTL). Retrofitting translation into a stored schema is expensive.

## Decision
Structure is shared across languages; only content is translated.
- `site.default_language` and `site.languages`.
- Sections keep default-language values in `props`. Translations live in a sparse `i18n: {lang: {prop: value}}` override map; only fields tagged `group: content` are translatable. Missing translations fall back to the default language (and the editor flags them).
- Pages and `site` settings (nav labels, SEO, business text) use the same override pattern. Page slugs can be overridden per language.
- Output: default language at `/`, others at `/<lang>/...`, with `hreflang` links, per-language sitemap entries and `<html lang dir>` (`dir=rtl` for RTL languages).
- Blog posts carry `lang` and a `translation_group` id; each translation is its own post.
- CSS uses logical properties (`margin-inline-start`, `text-align: start`) from M2 so RTL needs no separate stylesheet; alignment enum values are `start|center|end`.
- Fonts: curated pairings declare supported scripts.

## Consequences
- Adds the `i18n` field to the schema in M1 (empty by default); builder support lands in M5b; editor language switcher in M16.
- The content/design tags do double duty (permissions and translatability).
- Layout/structure per language cannot differ; accepted for v1.
