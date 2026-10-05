"""Glue between stored projects and the pure sitegen library."""

from sitegen import AssetFile, BuildResult, SiteDocument, build
from sqlalchemy.orm import Session

from app.projects.models import Project


def load_assets(db: Session, project: Project) -> dict[str, AssetFile]:
    """Uploaded files the builder may reference. Filled in by the assets milestone (M15)."""
    return {}


def build_project(db: Session, project: Project, doc: SiteDocument) -> BuildResult:
    return build(doc, load_assets(db, project))
