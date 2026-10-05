"""Imports every ORM model so Base.metadata (and Alembic) can see all tables."""

from app.assets.models import Asset  # noqa: F401
from app.auth.models import User, UserSession  # noqa: F401
from app.members.models import Invitation  # noqa: F401
from app.posts.models import BlogPost  # noqa: F401
from app.projects.models import Project, ProjectMember  # noqa: F401
