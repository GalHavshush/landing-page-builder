# ADR 011: Curated system font stacks (self-hosted web fonts deferred)

Status: accepted for v1, planned change

## Context
ADR 003 said generated sites self-host their fonts. That needs vetted font files (licence, subsets
per script incl. Hebrew/Arabic) bundled into every export.

## Decision (v1)
Four curated stacks (sans, serif, humanist, rounded) built from fonts present on the visitor's
system. This makes sites fast, private (no font requests), and RTL-safe, but typography varies a
little by device.

## Next
Add `woff2` files for 2-3 open-licence families to `sitegen/static/fonts/`, `@font-face` rules in the
theme CSS, and copy only the used fonts into the export. The theme schema already names fonts by
key, so documents will not change.
