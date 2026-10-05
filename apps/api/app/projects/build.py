"""Glue between stored projects and the pure sitegen library."""

import json

from sitegen import AssetFile, BuildResult, SiteDocument, build
from sitegen.posts import Post as GenPost
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets.models import Asset
from app.assets.storage import Storage, get_storage
from app.posts.models import BlogPost
from app.projects.models import Project


def published_posts(db: Session, project: Project) -> list[GenPost]:
    """Published posts as generator inputs. Drafts never reach a built site."""
    rows = db.scalars(
        select(BlogPost).where(BlogPost.project_id == project.id, BlogPost.status == "published")
    )
    return [
        GenPost(
            id=p.id,
            lang=p.lang,
            translation_group=p.translation_group,
            slug=p.slug,
            title=p.title,
            excerpt=p.excerpt,
            body_md=p.body_md,
            cover=p.cover_asset_id,
            published_at=p.published_at,
        )
        for p in rows
    ]


def referenced_assets(
    db: Session, project: Project, doc: SiteDocument, posts: list[GenPost] | None = None
) -> list[Asset]:
    """Assets the site actually uses (unused uploads are not shipped in exports)."""
    text = json.dumps(doc.model_dump(mode="json"))
    for p in posts or []:
        text += f" {p.cover or ''} {p.body_md}"
    rows = db.scalars(select(Asset).where(Asset.project_id == project.id))
    return [a for a in rows if a.id in text]


def load_assets(
    db: Session,
    project: Project,
    doc: SiteDocument,
    storage: Storage | None = None,
    posts: list[GenPost] | None = None,
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
        for a in referenced_assets(db, project, doc, posts)
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
) -> tuple[BuildResult, list[GenPost]]:
    posts = published_posts(db, project)
    return build(doc, load_assets(db, project, doc, storage, posts), posts), posts
