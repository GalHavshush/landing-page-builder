from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sitegen.models import new_id
from sitegen.posts import Post as GenPost
from sitegen.preview import render_post_preview
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.assets.models import Asset
from app.config import get_settings
from app.db import get_db, utcnow
from app.posts.models import BlogPost
from app.posts.schemas import PostIn, PostOut, PostPreviewIn, TranslateIn
from app.projects.build import preview_assets, published_posts
from app.projects.deps import EDIT_CONTENT, VIEW, Access
from app.projects.routes import parse_document

router = APIRouter(tags=["posts"])


def _languages(project) -> list[str]:
    return list(project.draft_doc.get("site", {}).get("languages", ["en"]))


def _check(db: Session, access: Access, body: PostIn) -> None:
    if body.lang not in _languages(access.project):
        raise HTTPException(422, f"The site has no {body.lang!r} language")
    if body.cover_asset_id:
        asset = db.get(Asset, body.cover_asset_id)
        if asset is None or asset.project_id != access.project.id:
            raise HTTPException(422, "Unknown cover image")


def _get(db: Session, access: Access, post_id: str) -> BlogPost:
    post = db.get(BlogPost, post_id)
    if post is None or post.project_id != access.project.id:
        raise HTTPException(404, "Post not found")
    return post


def _apply(post: BlogPost, body: PostIn) -> None:
    post.lang, post.title, post.slug = body.lang, body.title, body.slug
    post.excerpt, post.body_md, post.cover_asset_id = (
        body.excerpt,
        body.body_md,
        body.cover_asset_id,
    )
    if body.status == "published":
        # the first publish stamps the date unless the author chose one
        post.published_at = body.published_at or post.published_at or utcnow()
    else:
        post.published_at = body.published_at or post.published_at
    post.status = body.status
    post.updated_at = utcnow()


def _save(db: Session, post: BlogPost) -> BlogPost:
    try:
        db.add(post)
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            409, "Another post in this language already uses this URL name"
        ) from exc
    return post


@router.get("/projects/{project_id}/posts", response_model=list[PostOut])
def list_posts(access: Access = VIEW, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(BlogPost)
        .where(BlogPost.project_id == access.project.id)
        .order_by(BlogPost.updated_at.desc())
    )
    return list(rows)


@router.post("/projects/{project_id}/posts", response_model=PostOut, status_code=201)
def create_post(body: PostIn, access: Access = EDIT_CONTENT, db: Session = Depends(get_db)):
    _check(db, access, body)
    post = BlogPost(
        id=new_id("post"),
        project_id=access.project.id,
        translation_group=new_id("grp"),
        created_by=access.user.id,
        lang=body.lang,
        title=body.title,
        slug=body.slug,
    )
    _apply(post, body)
    return _save(db, post)


@router.get("/projects/{project_id}/posts/{post_id}", response_model=PostOut)
def get_post(post_id: str, access: Access = VIEW, db: Session = Depends(get_db)):
    return _get(db, access, post_id)


@router.put("/projects/{project_id}/posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: str, body: PostIn, access: Access = EDIT_CONTENT, db: Session = Depends(get_db)
):
    post = _get(db, access, post_id)
    _check(db, access, body)
    _apply(post, body)
    return _save(db, post)


@router.delete("/projects/{project_id}/posts/{post_id}", status_code=204)
def delete_post(post_id: str, access: Access = EDIT_CONTENT, db: Session = Depends(get_db)):
    db.delete(_get(db, access, post_id))
    return Response(status_code=204)


@router.post(
    "/projects/{project_id}/posts/{post_id}/translate", response_model=PostOut, status_code=201
)
def translate_post(
    post_id: str, body: TranslateIn, access: Access = EDIT_CONTENT, db: Session = Depends(get_db)
):
    """Start a translation: a new draft in `lang`, linked to the original, with its text copied."""
    source = _get(db, access, post_id)
    if body.lang not in _languages(access.project):
        raise HTTPException(422, f"The site has no {body.lang!r} language")
    exists = db.scalar(
        select(BlogPost.id).where(
            BlogPost.translation_group == source.translation_group, BlogPost.lang == body.lang
        )
    )
    if exists:
        raise HTTPException(409, "This post already has a translation in that language")
    copy = BlogPost(
        id=new_id("post"),
        project_id=source.project_id,
        translation_group=source.translation_group,
        created_by=access.user.id,
        lang=body.lang,
        slug=source.slug,
        title=source.title,
        excerpt=source.excerpt,
        body_md=source.body_md,
        cover_asset_id=source.cover_asset_id,
        status="draft",
        published_at=source.published_at,
    )
    return _save(db, copy)


@router.post("/projects/{project_id}/posts/{post_id}/preview")
def preview_post(
    post_id: str, body: PostPreviewIn, access: Access = VIEW, db: Session = Depends(get_db)
) -> dict:
    """Render a post as it would look (using the draft text from the editor, not saved yet)."""
    post = _get(db, access, post_id)
    doc = parse_document(access.project.draft_doc)
    known = preview_assets(db, access.project)
    prefix = get_settings().media_url_prefix
    candidate = GenPost(
        id=post.id,
        lang=body.lang,
        translation_group=post.translation_group,
        slug=body.slug,
        title=body.title,
        excerpt=body.excerpt,
        body_md=body.body_md,
        cover=body.cover_asset_id,
        published_at=body.published_at or post.published_at or datetime.now().astimezone(),
    )
    try:
        result = render_post_preview(
            doc,
            candidate,
            asset_url=lambda i: f"{prefix}/{known[i][1]}" if i in known else "",
            assets={i: f for i, (f, _) in known.items()},
            all_posts=published_posts(db, access.project),
        )
    except KeyError as exc:
        raise HTTPException(422, "Unknown language") from exc
    return {"html": result.html, "issues": [i.__dict__ for i in result.issues]}
