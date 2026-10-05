"""Glue between stored projects and the pure sitegen library."""

import json

from sitegen import AssetFile, BuildResult, SiteDocument, build
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets.models import Asset
from app.assets.storage import Storage, get_storage
from app.projects.models import Project


def referenced_assets(db: Session, project: Project, doc: SiteDocument) -> list[Asset]:
    """Assets the document actually uses (unused uploads are not shipped in exports)."""
    text = json.dumps(doc.model_dump(mode="json"))
    rows = db.scalars(select(Asset).where(Asset.project_id == project.id))
    return [a for a in rows if a.id in text]


def load_assets(
    db: Session, project: Project, doc: SiteDocument, storage: Storage | None = None
) -> dict[str, AssetFile]:
    storage = storage or get_storage()
    return {
        a.id: AssetFile(
            filename=a.original_filename,
            data=storage.get(a.storage_key),
            mime=a.mime,
            width=a.width,
            height=a.height,
        )
        for a in referenced_assets(db, project, doc)
    }


def preview_assets(db: Session, project: Project) -> dict[str, tuple[AssetFile, str]]:
    """For the editor preview: dimensions plus the storage key (no file bytes are read)."""
    rows = db.scalars(select(Asset).where(Asset.project_id == project.id))
    return {
        a.id: (AssetFile(a.original_filename, b"", a.mime, a.width, a.height), a.storage_key)
        for a in rows
    }


def build_project(
    db: Session, project: Project, doc: SiteDocument, storage: Storage | None = None
) -> BuildResult:
    return build(doc, load_assets(db, project, doc, storage))
