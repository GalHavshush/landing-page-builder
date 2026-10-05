"""Imports every ORM model so Base.metadata (and Alembic) can see all tables."""

from app.auth.models import User, UserSession  # noqa: F401
