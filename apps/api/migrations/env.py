from alembic import context
from app import models  # noqa: F401
from app.config import get_settings
from app.db import Base, make_engine

config = context.config


def render_item(type_, obj, autogen_context):
    """Keep migrations free of app imports: render our custom column types as plain SQLAlchemy."""
    if type_ == "type" and type(obj).__name__ == "UTCDateTime":
        return "sa.DateTime(timezone=True)"
    return False


target_metadata = Base.metadata


def _url() -> str:
    # tests/tools can pass -x url=...; otherwise use the app settings
    return context.get_x_argument(as_dictionary=True).get("url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = make_engine(_url())
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
