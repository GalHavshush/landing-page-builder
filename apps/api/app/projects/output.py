import re

from fastapi import APIRouter, Depends, HTTPException, Response
from sitegen.export import make_zip
from sitegen.meta import editor_meta
from sitegen.preview import render_preview
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.db import get_db
from app.projects.build import build_project, load_assets
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
    try:
        result = render_preview(
            doc,
            body.page_id,
            body.lang,
            asset_url=lambda asset_id: f"/media/{asset_id}",
            assets=load_assets(db, access.project),
        )
    except KeyError as exc:
        raise HTTPException(404, f"Unknown page or language: {exc.args[0]}") from exc
    return PreviewOut(html=result.html, issues=[i.__dict__ for i in result.issues])


@router.post("/projects/{project_id}/export")
def export_zip(access: Access = VIEW, db: Session = Depends(get_db)):
    """Build the saved draft and return it as a ZIP: plain static files, deployable anywhere."""
    project = access.project
    doc = parse_document(project.draft_doc)
    result = build_project(db, project, doc)
    data = make_zip(result.files, doc)
    filename = re.sub(r"[^a-z0-9-]", "", project.slug) or "site"
    return Response(
        data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}.zip"'},
    )
