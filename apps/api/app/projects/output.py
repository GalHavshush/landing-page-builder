from fastapi import APIRouter, Depends, HTTPException, Response
from sitegen.fonts import FONTS_DIR
from sitegen.meta import editor_meta
from sitegen.preview import render_preview
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.config import get_settings
from app.db import get_db
from app.projects.build import preview_assets, published_posts
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


@router.get("/fonts/{path:path}", include_in_schema=False)
def bundled_font(path: str) -> Response:
    """Bundled web fonts for the editor's sandboxed preview iframe (public, immutable).

    The iframe has an opaque origin, so the browser fetches its fonts cross-origin and needs CORS.
    """
    file = (FONTS_DIR / path).resolve()
    if FONTS_DIR.resolve() not in file.parents or file.suffix != ".woff2" or not file.is_file():
        raise HTTPException(404, "Not found")
    return Response(
        file.read_bytes(),
        media_type="font/woff2",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Access-Control-Allow-Origin": "*",
            "X-Content-Type-Options": "nosniff",
        },
    )


def _render(db: Session, access: Access, doc, page_id: str, lang: str | None, interactive: bool):
    known = preview_assets(db, access.project)
    prefix = get_settings().media_url_prefix
    try:
        result = render_preview(
            doc,
            page_id,
            lang,
            asset_url=lambda asset_id: (
                f"{prefix}/{known[asset_id][1]}" if asset_id in known else ""
            ),
            assets={asset_id: file for asset_id, (file, _) in known.items()},
            posts=published_posts(db, access.project),
            font_base=f"{get_settings().media_url_prefix.rsplit('/', 1)[0]}/fonts/",
            interactive=interactive,
        )
    except KeyError as exc:
        raise HTTPException(404, f"Unknown page or language: {exc.args[0]}") from exc
    return PreviewOut(html=result.html, issues=[i.__dict__ for i in result.issues])


@router.post("/projects/{project_id}/preview", response_model=PreviewOut)
def preview(body: PreviewIn, access: Access = VIEW, db: Session = Depends(get_db)):
    """Render a page of the document the editor currently holds (not necessarily saved yet)."""
    return _render(db, access, parse_document(body.doc), body.page_id, body.lang, body.interactive)


@router.get("/projects/{project_id}/live", response_model=PreviewOut)
def live(
    page_id: str | None = None,
    lang: str | None = None,
    access: Access = VIEW,
    db: Session = Depends(get_db),
):
    """Interactive preview of the saved draft (the dashboard's thumbnails and quick preview)."""
    doc = parse_document(access.project.draft_doc)
    return _render(db, access, doc, page_id or doc.pages[0].id, lang, True)
