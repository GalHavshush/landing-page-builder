import hashlib
import json
import re
import secrets
from pathlib import PurePath

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field
from sitegen.models import new_id
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets.images import InvalidImage, process_image
from app.assets.models import Asset
from app.assets.storage import Storage, StorageNotFound, get_storage
from app.config import get_settings
from app.db import get_db
from app.posts.models import BlogPost
from app.projects.deps import EDIT_CONTENT, VIEW, Access

router = APIRouter(tags=["assets"])


class AssetOut(BaseModel):
    id: str
    filename: str
    url: str
    thumb_url: str
    width: int
    height: int
    size_bytes: int
    alt_default: str


class AssetPatch(BaseModel):
    alt_default: str = Field(max_length=300)


def media_url(key: str) -> str:
    return f"{get_settings().media_url_prefix}/{key}"


def asset_out(a: Asset) -> AssetOut:
    return AssetOut(
        id=a.id,
        filename=a.original_filename,
        url=media_url(a.storage_key),
        thumb_url=media_url(a.thumb_key),
        width=a.width,
        height=a.height,
        size_bytes=a.size_bytes,
        alt_default=a.alt_default,
    )


def delete_files(storage: Storage, asset: Asset) -> None:
    for key in {asset.storage_key, asset.thumb_key, *(v["key"] for v in asset.variants or [])}:
        storage.delete(key)


def _clean_name(name: str) -> str:
    stem = PurePath(name or "image").stem
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-")[:80] or "image"


@router.post("/projects/{project_id}/assets", response_model=AssetOut, status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    access: Access = EDIT_CONTENT,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
):
    limit = get_settings().max_upload_bytes
    data = await file.read(limit + 1)  # never read more than the limit into memory
    if len(data) > limit:
        raise HTTPException(413, f"Images can be at most {limit // (1024 * 1024)} MB")
    try:
        processed = process_image(data)
    except InvalidImage as exc:
        raise HTTPException(422, str(exc)) from exc

    name = _clean_name(file.filename or "")
    token = secrets.token_urlsafe(16)  # unguessable: files are public by URL, like on a CDN
    base = f"p{access.project.id}/{token}"
    variant_rows = [{"width": w, "key": f"{base}/{name}-{w}.webp"} for w, _ in processed.variants]
    asset = Asset(
        id=new_id("asset"),
        project_id=access.project.id,
        uploaded_by=access.user.id,
        storage_key=f"{base}/{name}.webp",
        thumb_key=variant_rows[0]["key"] if variant_rows else f"{base}/{name}.webp",
        original_filename=f"{name}.webp",
        mime="image/webp",
        size_bytes=len(processed.main),
        width=processed.width,
        height=processed.height,
        sha256=hashlib.sha256(processed.main).hexdigest(),
        alt_default="",
        variants=variant_rows,
        color=processed.color,
    )
    storage.put(asset.storage_key, processed.main, "image/webp")
    for (_, data), row in zip(processed.variants, variant_rows, strict=True):
        storage.put(row["key"], data, "image/webp")
    db.add(asset)
    db.flush()
    return asset_out(asset)


@router.get("/projects/{project_id}/assets", response_model=list[AssetOut])
def list_assets(access: Access = VIEW, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Asset).where(Asset.project_id == access.project.id).order_by(Asset.created_at.desc())
    )
    return [asset_out(a) for a in rows]


def _get_asset(db: Session, project_id: int, asset_id: str) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None or asset.project_id != project_id:
        raise HTTPException(404, "Asset not found")
    return asset


@router.patch("/projects/{project_id}/assets/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: str, body: AssetPatch, access: Access = EDIT_CONTENT, db: Session = Depends(get_db)
):
    asset = _get_asset(db, access.project.id, asset_id)
    asset.alt_default = body.alt_default
    return asset_out(asset)


@router.delete("/projects/{project_id}/assets/{asset_id}", status_code=204)
def delete_asset(
    asset_id: str,
    access: Access = EDIT_CONTENT,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
):
    asset = _get_asset(db, access.project.id, asset_id)
    used_in_posts = db.scalar(
        select(BlogPost.id).where(
            BlogPost.project_id == access.project.id,
            (BlogPost.cover_asset_id == asset_id) | BlogPost.body_md.contains(asset_id),
        )
    )
    if asset_id in json.dumps(access.project.draft_doc) or used_in_posts:
        raise HTTPException(409, "This image is used on the site. Remove it there first.")
    delete_files(storage, asset)
    db.delete(asset)
    return Response(status_code=204)


@router.get("/media/{key:path}", include_in_schema=False)
def serve_media(key: str, storage: Storage = Depends(get_storage)):
    """Public file serving for local storage / dev. (With S3 + a CDN, browsers skip this.)"""
    try:
        data = storage.get(key)
    except StorageNotFound as exc:
        raise HTTPException(404, "Not found") from exc
    return Response(
        data,
        media_type="image/webp",  # everything stored is a re-encoded WebP
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "X-Content-Type-Options": "nosniff",
        },
    )
