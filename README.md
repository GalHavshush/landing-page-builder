# Site Builder

A small SaaS for building simple, polished **static** websites with a constrained visual editor
(pages made of ready-made sections, controlled design options, no arbitrary HTML/CSS). Sites export
as a ZIP of plain HTML/CSS/assets that runs anywhere, with no vendor lock-in. Built to be used both as
a product and as an agency tool: invite a client who gets a simplified, content-only editor.

Start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); decisions are in [docs/adr/](docs/adr/).

## Run it

```bash
uv sync --all-packages --all-groups     # Python deps (uv: https://docs.astral.sh/uv/)
docker compose up -d postgres           # or use any PostgreSQL; SQLite also works for a quick look
cd apps/api
uv run alembic upgrade head
uv run uvicorn app.main:app --reload    # API on :8000
# second terminal
cd apps/web && npm install && npm run dev   # editor on http://localhost:5173
```

Without Docker, for a quick try: `BUILDER_DATABASE_URL=sqlite:///dev.db` before the two `uv run` commands.
Settings are environment variables prefixed `BUILDER_` (see `.env.example` and `apps/api/app/config.py`).

The generator also works on its own, no server needed:

```bash
uv run python -m sitegen init warm site.json --name "My Bakery"
uv run python -m sitegen build site.json out/ --zip site.zip
```

## Develop

```bash
uv run pytest                  # 250+ Python tests (generator + API, on in-memory SQLite)
BUILDER_TEST_DATABASE_URL=postgresql+psycopg://... uv run pytest apps/api   # same suite on PostgreSQL
uv run ruff check . && uv run ruff format --check .
cd apps/web && npm test && npm run typecheck && npm run build
npm run gen                    # after changing backend models: regenerate the TypeScript types
```

## Layout

- `packages/sitegen/` the pure site generator: schema, sections, themes, renderer, export, CLI
- `apps/api/` FastAPI backend (auth, projects, assets, posts, members, exports) + Alembic migrations
- `apps/web/` React editor
- `docs/` architecture and decision records

Full-stack containers: `docker compose --profile app up --build` (see the note in `docker-compose.yml`).
