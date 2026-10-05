# ADR 007: Synchronous SQLAlchemy; SQLite for fast tests

Status: accepted

## Decision
- The API uses **synchronous** SQLAlchemy 2.0 sessions and plain `def` endpoints. FastAPI runs them in a threadpool. This is simpler to read, debug and test than async ORM code, and is plenty for this workload. The CPU-heavy parts (site builds, image processing) are synchronous anyway.
- One DB session per request via the `get_db` dependency (commit on success, rollback on error).
- Production and development run **PostgreSQL**; JSON columns use JSONB there (`JSONType`). The unit tests run on in-memory SQLite so they need no services. Anything Postgres-specific must go behind `JSONType`-style variants. Alembic migrations are checked against SQLite in tests and should be run against Postgres before release (`docker compose up -d postgres && alembic upgrade head`).

## Consequences
Fast, dependency-free tests. A small risk that SQLite and Postgres differ (case sensitivity, constraint behaviour); mitigated by running the suite against Postgres in CI when a `BUILDER_TEST_DATABASE_URL` is provided.
