# ADR 001: One renderer for preview and output

Status: accepted

## Context
Editor previews and published sites usually drift when implemented twice.

## Decision
`sitegen` (Python + Jinja2) is the only renderer. The editor posts the in-memory document to `/preview` (debounced) and shows the returned HTML in a sandboxed iframe. A preview-only script adds hover outlines and click-to-select via `postMessage`; it is never part of the output.

## Consequences
- Preview equals output by construction; no Node render worker.
- Mobile preview uses real media queries (iframe width).
- No inline text editing on the canvas; edits happen in the properties panel. Each update costs a round trip (~50-150 ms).
- Revisit only if inline editing becomes essential; the document schema would not change.

Alternatives rejected: React SSR (second language in backend), Jinja + React (guaranteed drift).
