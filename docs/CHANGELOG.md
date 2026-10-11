# Changelog and local setup

## Run it locally

You need [uv](https://docs.astral.sh/uv/), Node.js with npm, and Docker (for Postgres).

**1. One-time setup**

| Where | Command | What it does |
|---|---|---|
| project root | `uv sync --all-packages --all-groups` | installs the Python packages |
| project root | `docker compose up -d postgres` | starts the database (data lives in a Docker volume) |
| `apps/api` | `uv run alembic upgrade head` | creates the database tables |
| `apps/web` | `npm install` | installs the web packages |

No Docker? Put `BUILDER_DATABASE_URL=sqlite:///dev.db` in front of the `alembic` and `uvicorn` commands.

**2. Start the app** (two terminals, both stay running)

| Terminal | Folder | Command | Result |
|---|---|---|---|
| 1, API | `apps/api` | `uv run uvicorn app.main:app --reload` | API on http://localhost:8000 |
| 2, editor | `apps/web` | `npm run dev` | editor on **http://localhost:5173** (open this one) |

**3. Everyday commands**

| Folder | Command | Purpose |
|---|---|---|
| project root | `uv run pytest` | Python tests (generator and API) |
| project root | `uv run ruff check . && uv run ruff format --check .` | lint and format check |
| `apps/web` | `npm test` / `npm run typecheck` / `npm run build` | web tests, types, production build |
| `apps/web` | `npm run gen` | regenerate the TypeScript API types after changing backend models |
| project root | `docker compose stop postgres` / `docker compose start postgres` | stop or start the database **without deleting it** |

Good to know:
- Never run `docker compose down -v`: it deletes the database volume. If the tables ever go missing (every login returns a 500), run `uv run alembic upgrade head` in `apps/api`.
- The API's auto-reload only watches `apps/api`. After changing the generator in `packages/sitegen`, restart the API (or touch a file under `apps/api`).
- Settings are environment variables prefixed `BUILDER_` (see `.env.example` and `apps/api/app/config.py`).

## How to use this changelog

Add one entry per change, **newest first**. Put today's entry at the top of the list below, under a `### YYYY-MM-DD` heading (add to that heading if today's already there). Never reorder or edit old entries except to fix a mistake. Keep each entry to a line or two: what changed and why it matters. Add the commit hash when there is one.

## Changes

### 2026-10-11
- Added this changelog and the local-run instructions.

### 2026-10-08
- **Blog posts now open in the preview.** Post links in the interactive preview were dead; they now open the post, and "Back to blog" returns to the page. (`21ab623`)
- **Social links moved to the contact section**, shown as round icon links with a logo for each network (Instagram, Facebook, LinkedIn, X, YouTube, TikTok, WhatsApp, Pinterest; a globe for any other). The footer no longer lists them. `.DS_Store` is now git-ignored. (`ffe7c60`)
- **Guided new-site form** at `/new`: a step-by-step form (Hebrew or English, with a live preview) that fills the editor from the owner's answers. The old template box stays behind "Start from a template". New API endpoints `POST /projects/from-brief` and `POST /projects/preview-brief`. (`01d5c2c`)

### 2026-10-07
- Merged the QA-fixes branch: the editor works on phones (one panel at a time with a bottom bar), better accessibility (readable secondary text, labelled side panels), and clearer field labels. (`d93ced4`)
- Validation and hints: SEO fields have character counters and hard limits; email and colour fields explain invalid input and never save it; the website address must be https; the URL name field reverts when left invalid; invite emails are validated in the Share dialog.
- Editor polish: the section list shows a useful summary instead of "Empty", the preview hints at sections with nothing to show, the export dialog has "Export again", and the settings tab row scrolls so "Checks" is never clipped.
- Fixed the blog post preview ignoring the font base. (`d605084`)

### 2026-10-06
- Regenerated the API types for the `editor-meta` `lang` parameter. (`85b8b0e`)
- Login preferences menu, Hebrew as the default editor language, and placeholder text that follows the site's language. (`a95e5c3`)
- Hebrew placeholder content for every starter, section and page layout. (`4030a94`)
- Interactive site preview with a desktop/mobile toggle, and live thumbnails on the dashboard. (`efe858e`)
- Hebrew editor with right-to-left layout, a global settings page, and editor UI for the new features. (`57464c3`)
- Editor language and theme are stored on the user account. (`2813606`)
- Social links, page order, preview navigation jumps, and site languages chosen at creation. (`33e103b`)

### 2026-10-05
- Stopped tracking local upload data (`data/uploads/` is ignored).
- Visual QA harness in CI (overflow and accessibility checks) and accessible accent/brand text colours. (`5dec0e9`)
- Gallery lightbox and a theme animation setting. (`3526c43`)
- JSON-LD structured data, font fallback metrics, and a generated social card. (`684284f`)
- Stock photo search (Pexels) in the image library. (`4a2bda2`)
- Design checks panel in the editor. (`5132678`)
- Eight industry starters, page recipes and photo hints. (`ab0195a`)
- Style packs, look switcher, brand palette generator, count-aware grids. (`e6ba4f8`)
- New sections: team, hours, stats, logos, steps, call to action and before/after. (`b48e330`)
- Logo, favicon, header and footer variants, header CTA button, announcement bar. (`f471635`)
- Responsive images: `srcset` variants, focal point, placeholder colour, size warnings. (`42b7f76`)
- Nine more section layouts (hero banner, numbered features, alternating services and others). (`d992c76`)
- Bundled web fonts: seven open-licence families, self-hosted in every export. (`614065c`)

### Before 2026-10-05
- The first milestones (M0 to M21): the site generator, API, editor, blog, members and roles, and exports. See [ARCHITECTURE.md](ARCHITECTURE.md) and the decision records in [adr/](adr/).
