import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.projects.models import Project


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:60] or "site"


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    slug, n = base, 1
    while db.scalar(select(Project.id).where(Project.slug == slug)):
        n += 1
        slug = f"{base}-{n}"
    return slug
