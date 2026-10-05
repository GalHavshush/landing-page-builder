import re

from fastapi import APIRouter, Depends, HTTPException, Response
from sitegen.export import make_zip
from sitegen.meta import editor_meta
from sitegen.preview import render_preview
from sqlalchemy.orm import Session

from app.assets.storage import Storage, get_storage
from app.auth.deps import get_current_user
from app.auth.models import User
from app.config import get_settings
from app.db import get_db
from app.projects.build import build_project, preview_assets
from app.projects.deps import VIEW, Access
from app.projects.routes import parse_document
from app.projects.schemas import PreviewIn, PreviewOut

router = APIRouter(tags=["output"])

_META = None


@router.get("/editor-meta")
def get_editor_meta(_: User = Depends(get_current_user)) -> dict:
    """Section types, field hints, themes constants: everything the editor UI is generated from."""
    global _META
    if _META is None:
        _META = editor_meta()
    return _META


@router.post("/projects/{project_id}/preview", response_model=PreviewOut)
def preview(body: PreviewIn, access: Access = VIEW, db: Session = Depends(get_db)):
    """Render a page of the document the editor currently holds (not necessarily saved yet)."""
    doc = parse_document(body.doc)
    known = preview_assets(db, access.project)
    prefix = get_settings().media_url_prefix
    try:
        result = render_preview(
            doc,
            body.page_id,
            body.lang,
            asset_url=lambda asset_id: (
                f"{prefix}/{known[asset_id][1]}" if asset_id in known else ""
            ),
            assets={asset_id: file for asset_id, (file, _) in known.items()},
        )
    except KeyError as exc:
        raise HTTPException(404, f"Unknown page or language: {exc.args[0]}") from exc
    return PreviewOut(html=result.html, issues=[i.__dict__ for i in result.issues])


@router.post("/projects/{project_id}/export")
def export_zip(
    access: Access = VIEW,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
):
    """Build the saved draft and return it as a ZIP: plain static files, deployable anywhere."""
    project = access.project
    doc = parse_document(project.draft_doc)
    result = build_project(db, project, doc, storage)
    data = make_zip(result.files, doc)
    filename = re.sub(r"[^a-z0-9-]", "", project.slug) or "site"
    return Response(
        data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}.zip"'},
    )
