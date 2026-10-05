# Architecture

A small SaaS for building simple, polished **static** websites with a constrained, no-code visual editor.
Positioning: a lightweight visual CMS + static output for small businesses, freelancers and agencies. Not a Webflow/Wix competitor.

Principles: very easy to use, hard to make ugly, static output, exportable, no lock-in, simple over clever.

Decisions are recorded in [`docs/adr/`](adr/). This document is the overview.

## Decisions made so far

| # | Decision | ADR |
|---|---|---|
| 1 | One Python/Jinja renderer produces preview and output; preview is an iframe | [001](adr/001-single-renderer.md) |
| 2 | A website is one JSON document (JSONB), not pages/sections tables | [002](adr/002-site-document.md) |
| 3 | Static output cannot run backend code (forms, blog timing, embeds) | [003](adr/003-static-limits.md) |
| 4 | v1 ships ZIP export only; automatic publishing is post-v1 | [004](adr/004-zip-first.md) |
| 5 | Agency mode first: roles and client content editor are early | [005](adr/005-agency-first.md) |
| 6 | Multi-language is in the schema from day one | [006](adr/006-multi-language.md) |

## High-level shape

```
Browser: React SPA (dashboard + editor)
   │  JSON/REST (cookie session)        ▲ HTML (iframe srcdoc)
FastAPI monolith ── calls ──► sitegen (pure library: doc + posts + assets → {path: bytes})
   │
Postgres (accounts, docs, posts)    Object storage (uploads, export ZIPs)
```

- `sitegen` has **no web or DB imports**. It is used by preview, ZIP export, the CLI, and (later) deployers.
- The SaaS is a monolith. No microservices, no Redis/Celery in v1.

## Stack

Backend: FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, PostgreSQL, Jinja2, markdown-it-py + nh3, Pillow, argon2-cffi, boto3 (S3 API; MinIO locally).
Frontend: React + TypeScript + Vite, TanStack Query, Zustand + Immer, dnd-kit, Tailwind + Radix (editor chrome only), Tiptap (blog, later), openapi-typescript.
Tooling: uv, ruff, pytest, pre-commit, Docker Compose, GitHub Actions.
Generated sites: hand-written CSS with custom properties, near-zero JS, self-hosted fonts.

## Data model (tables)

```
users, sessions
projects(id, name, slug, template_id, draft_doc JSONB, doc_version, revision, ...)
project_members(project_id, user_id, role: owner|designer|editor)
invitations(id, project_id, email, role, token_hash, expires_at, accepted_at)
assets(id, project_id, storage_key, mime, size, width, height, sha256, ...)
posts(id, project_id, lang, translation_group, slug, title, status, body_md, ...)
exports(id, project_id, triggered_by, doc_revision, artifact_key, created_at)
```

No `pages`/`sections`/`themes` tables: they live in `draft_doc` (ADR 002). Templates are files in the repo.
Post-v1: `deploy_targets`, `deployments`, `domains`.

## Site document (sketch)

```json
{
  "schema_version": 1,
  "site": {
    "name": "...", "default_language": "en", "languages": ["en", "he"],
    "base_url": "https://example.com",
    "business": {"phone": "", "email": "", "address": "", "hours": [], "social": {}},
    "seo": {}, "nav": [], "footer": {}
  },
  "theme": {"template": "warm", "palette": {}, "fonts": {}, "radius": "md", "button_style": "solid", "spacing": "normal"},
  "pages": [{
    "id": "pg_home", "slug": "", "title": "Home", "seo": {},
    "sections": [{
      "id": "sec_...", "type": "hero", "variant": "split",
      "props": {}, "style": {"background": "default", "spacing": "spacious", "align": "start"},
      "i18n": {"he": {"heading": "..."}}
    }]
  }]
}
```

Rules: stable IDs everywhere; colors are palette token names, not hex; every option is an enum; links are structured (`{"page": id}` / `{"url": ...}`); sections are a Pydantic discriminated union on `type`.

## Sections

Each section type is a folder in `sitegen/sections/<type>/` with `model.py` (props), `template.html.j2`, `style.css`, registered in a registry. Prop fields are tagged `group: content | design` and `control: ...`; the tags drive the properties panel, the client's content-only editor, server-side permission checks, and which fields are translatable.

MVP set: Hero, Text, Features, Services, Gallery, Testimonials, FAQ, Pricing, Contact, YouTube, Map, Footer, Blog list.

## Build pipeline

`build(doc, posts, assets) -> dict[path, bytes]`, pure and deterministic:
validate/migrate → semantic checks → resolve assets → theme.css + used-section CSS → render pages per language → blog → sitemap/robots/404 → return files.
Relative URLs, self-hosted fonts, must work from `file://`.

## Editor

Three panes: pages + section list | iframe preview (desktop/mobile) | properties. Zustand store holds the doc; all mutations are small pure commands run through Immer (patches give undo/redo). Debounced autosave with `revision` (409 on conflict). Debounced `POST /preview` returns HTML for the iframe; a preview-only script handles hover outlines and click-to-select via `postMessage`.

## Auth and permissions

Email + password (argon2), server-side sessions, httpOnly SameSite=Lax cookie, CSRF header. Roles per project: owner / designer / editor. One permission matrix function; the server diffs saves against field `group` tags so an editor cannot change design props or structure.

## Export (v1)

`POST /projects/{id}/export` builds the draft and returns a ZIP (plain HTML/CSS/assets/fonts, README, `export.json` with the site document for re-import). The artifact is stored in an `exports` row.

## Post-v1

Cloudflare Pages deploy (BYO token) behind a `Deployer` interface, background worker, custom domains, managed multi-tenant hosting, inline canvas editing.

## Not in v1

Freeform canvas, custom HTML/CSS/JS, realtime collaboration, billing/teams, e-commerce, hosted form storage, analytics, template marketplace, AI generation, scheduled publishing, OAuth/2FA, automatic deployment, custom domains.

## Repository layout

```
apps/api/            FastAPI app (from M6)
apps/web/            React editor (from M10)
packages/sitegen/    pure Python generator + CLI
docs/adr/            decision records
docker-compose.yml   postgres + minio for local dev
```

## Roadmap

**A. Generator (no web app)**
- M0 Repo skeleton (this commit)
- M1 Schema + first render (Hero, Text), golden test
- M2 Theme tokens, base layout, common style options, RTL-safe CSS
- M3 Sections batch 1 (Features, Services, Testimonials, FAQ, Footer)
- M4 Multi-page, SEO, sitemap/robots/404, CLI, ZIP
- M5 Schema versioning + migrations + semantic validation
- M5b Language support in the builder (per-language output, hreflang, `dir`)

**B. Backend**
- M6 API skeleton, DB, Alembic, test fixtures
- M7 Auth
- M8 Projects + doc save with optimistic locking
- M9 Preview + export endpoints

**C. Editor**
- M10 Web skeleton + generated types
- M11 Read-only editor shell
- M12 Editing core: commands, dnd, autosave, undo/redo
- M13 Properties panel v1
- M14 Repeaters + remaining controls
- M15 Assets
- M16 Site settings, theme, SEO, language switcher

**D. Content and agency features**
- M17 Remaining sections + form endpoint config
- M18 Blog (per-language posts)
- M19 Members, invite links, roles, content-only client editor
- M20 Exports table + "download last export"
- M21 Polish, extra templates, ship the SaaS

Each milestone: small, runnable, tested, committed on its own.
