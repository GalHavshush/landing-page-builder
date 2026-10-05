"""Database wiring: engine, session-per-request, declarative base."""

from collections.abc import Iterator
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, TypeDecorator, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# JSONB on Postgres (indexable, binary), plain JSON elsewhere (SQLite in tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")


class UTCDateTime(TypeDecorator):
    """Timezone-aware UTC datetimes on every backend (SQLite drops tzinfo, so restore it)."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            raise ValueError("naive datetime; use datetime.now(UTC)")
        return value.astimezone(UTC) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, **kwargs)


_engine = None
_SessionLocal = None


def get_sessionmaker() -> sessionmaker[Session]:
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = make_engine(get_settings().database_url)
        _SessionLocal = sessionmaker(_engine, expire_on_commit=False)
    return _SessionLocal


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, committed on success, rolled back on error."""
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
