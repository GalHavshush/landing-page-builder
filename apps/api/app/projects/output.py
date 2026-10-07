from fastapi import APIRouter, Depends, HTTPException, Response
from sitegen.fonts import FONTS_DIR
from sitegen.meta import editor_meta
from sitegen.preview import render_post_preview, render_preview
from sitegen.strings import LANGUAGE_NAMES
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.config import get_settings
from app.db import get_db
from app.projects.build import preview_assets, published_posts
from app.projects.deps import VIEW, Access
from app.projects.routes import brief_document, parse_document
from app.projects.schemas import BriefPreviewIn, PreviewIn, PreviewOut

router = APIRouter(tags=["output"])

_META: dict[str | None, dict] = {}


@router.get("/editor-meta")
def get_editor_meta(lang: str | None = None, _: User = Depends(get_current_user)) -> dict:
    """Section types, field hints, themes constants: everything the editor UI is generated from.

    `lang`: the language of the placeholder text in new sections and pages (the site's language).
    """
    lang = lang if lang in LANGUAGE_NAMES else None
    if lang not in _META:
        _META[lang] = editor_meta(lang)
    return _META[lang]


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


def _render(
    db: Session,
    access: Access,
    doc,
    page_id: str,
    lang: str | None,
    interactive: bool,
    post_id: str | None = None,
):
    known = preview_assets(db, access.project)
    prefix = get_settings().media_url_prefix
    options = dict(
        asset_url=lambda asset_id: f"{prefix}/{known[asset_id][1]}" if asset_id in known else "",
        assets={asset_id: file for asset_id, (file, _) in known.items()},
        font_base=f"{get_settings().media_url_prefix.rsplit('/', 1)[0]}/fonts/",
    )
    posts = published_posts(db, access.project)
    try:
        if post_id is not None:
            post = next((p for p in posts if p.id == post_id), None)
            if post is None:
                raise HTTPException(404, "Unknown post")
            result = render_post_preview(
                doc, post, all_posts=posts, interactive=interactive, **options
            )
        else:
            result = render_preview(
                doc, page_id, lang, posts=posts, interactive=interactive, **options
            )
    except KeyError as exc:
        raise HTTPException(404, f"Unknown page or language: {exc.args[0]}") from exc
    return PreviewOut(html=result.html, issues=[i.__dict__ for i in result.issues])


@router.post("/projects/{project_id}/preview", response_model=PreviewOut)
def preview(body: PreviewIn, access: Access = VIEW, db: Session = Depends(get_db)):
    """Render a page of the document the editor currently holds (not necessarily saved yet)."""
    return _render(
        db,
        access,
        parse_document(body.doc),
        body.page_id,
        body.lang,
        body.interactive,
        body.post_id,
    )


@router.get("/projects/{project_id}/live", response_model=PreviewOut)
def live(
    page_id: str | None = None,
    lang: str | None = None,
    post_id: str | None = None,
    access: Access = VIEW,
    db: Session = Depends(get_db),
):
    """Interactive preview of the saved draft (the dashboard's thumbnails and quick preview)."""
    doc = parse_document(access.project.draft_doc)
    return _render(db, access, doc, page_id or doc.pages[0].id, lang, True, post_id)


@router.post("/projects/preview-brief", response_model=PreviewOut)
def preview_brief(body: BriefPreviewIn, _: User = Depends(get_current_user)):
    """Live preview for the guided new-site form: renders the brief without saving anything."""
    doc = brief_document(body.brief)
    try:
        result = render_preview(
            doc,
            body.page_id or doc.pages[0].id,
            font_base=f"{get_settings().media_url_prefix.rsplit('/', 1)[0]}/fonts/",
            interactive=True,
        )
    except KeyError as exc:
        raise HTTPException(404, f"Unknown page: {exc.args[0]}") from exc
    return PreviewOut(html=result.html, issues=[i.__dict__ for i in result.issues])
