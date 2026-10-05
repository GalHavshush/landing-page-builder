import re
import secrets

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sitegen.export import make_zip
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets.storage import Storage, StorageNotFound, get_storage
from app.auth.models import User
from app.db import get_db
from app.exports.models import SiteExport
from app.projects.build import build_project
from app.projects.deps import EXPORT, Access
from app.projects.routes import parse_document

router = APIRouter(tags=["exports"])
KEEP_LAST = 10  # older artifacts are deleted so storage does not grow without bound


class ExportOut(BaseModel):
    id: int
    doc_revision: int
    size_bytes: int
    file_count: int
    created_at: str
    created_by: str
    issues: list[dict]


def _out(e: SiteExport, db: Session) -> ExportOut:
    user = db.get(User, e.created_by)
    return ExportOut(
        id=e.id,
        doc_revision=e.doc_revision,
        size_bytes=e.size_bytes,
        file_count=e.file_count,
        created_at=e.created_at.isoformat(),
        created_by=(user.name or user.email) if user else "",
        issues=e.issues,
    )


@router.post("/projects/{project_id}/exports", response_model=ExportOut, status_code=201)
def create_export(
    access: Access = EXPORT, db: Session = Depends(get_db), storage: Storage = Depends(get_storage)
):
    """Build the saved site, keep the ZIP, and report anything the builder noticed."""
    project = access.project
    doc = parse_document(project.draft_doc)
    result, posts = build_project(db, project, doc, storage)
    data = make_zip(result.files, doc, posts)
    key = f"exports/p{project.id}/{secrets.token_urlsafe(12)}.zip"
    storage.put(key, data, "application/zip")
    export = SiteExport(
        project_id=project.id,
        created_by=access.user.id,
        doc_revision=project.revision,
        artifact_key=key,
        size_bytes=len(data),
        file_count=len(result.files),
        issues=[i.__dict__ for i in result.issues if i.level in ("warning", "info")],
    )
    db.add(export)
    db.flush()
    _prune(db, storage, project.id)
    return _out(export, db)


def _prune(db: Session, storage: Storage, project_id: int) -> None:
    rows = list(
        db.scalars(
            select(SiteExport)
            .where(SiteExport.project_id == project_id)
            .order_by(SiteExport.id.desc())
        )
    )
    for old in rows[KEEP_LAST:]:
        storage.delete(old.artifact_key)
        db.delete(old)


@router.get("/projects/{project_id}/exports", response_model=list[ExportOut])
def list_exports(access: Access = EXPORT, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(SiteExport)
        .where(SiteExport.project_id == access.project.id)
        .order_by(SiteExport.id.desc())
    )
    return [_out(e, db) for e in rows]


@router.get("/projects/{project_id}/exports/{export_id}/download")
def download_export(
    export_id: int,
    access: Access = EXPORT,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
):
    export = db.get(SiteExport, export_id)
    if export is None or export.project_id != access.project.id:
        raise HTTPException(404, "Export not found")
    try:
        data = storage.get(export.artifact_key)
    except StorageNotFound as exc:
        raise HTTPException(410, "This export is no longer available") from exc
    name = re.sub(r"[^a-z0-9-]", "", access.project.slug) or "site"
    return Response(
        data,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{name}-{export.id}.zip"',
            "X-Content-Type-Options": "nosniff",
        },
    )
