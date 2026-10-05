# ADR 002: A website is one JSON document

Status: accepted

## Decision
Pages, sections, theme, site settings and SEO live in one JSONB document (`projects.draft_doc`), validated by Pydantic (discriminated union on section `type`). Only large or independently edited things get tables: assets, posts, exports.
Documents carry `schema_version`; migration functions exist from the start. Saves use an integer `revision` for optimistic concurrency (409 on conflict).

## Consequences
- Reorder/version/snapshot/export are trivial; undo/redo operates on one object.
- No cross-project queries over sections (not needed).
- Colors are palette token names; all options are enums; links are structured.
- Templates are files in the repo, not DB rows.
