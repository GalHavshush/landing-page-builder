# landing-page-builder

A small SaaS for building simple, polished, **static** websites with a constrained visual editor.
Static output, ZIP export, no lock-in. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/adr/](docs/adr/).

## Dev setup

```
uv sync --all-packages
uv run pytest
uv run ruff check . && uv run ruff format --check .
docker compose up -d        # postgres + minio (used from M6)
```

## Layout

- `packages/sitegen/` pure site generator (no web/DB imports)
- `apps/api/` FastAPI app (M6)
- `apps/web/` React editor (M10)
- `docs/` architecture and decision records
