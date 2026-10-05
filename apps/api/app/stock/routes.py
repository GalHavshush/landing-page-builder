from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.assets.images import InvalidImage
from app.assets.routes import AssetOut, asset_out, store_image
from app.assets.storage import Storage, get_storage
from app.config import get_settings
from app.db import get_db
from app.projects.deps import EDIT_CONTENT, Access
from app.ratelimit import limit_stock
from app.stock.provider import PexelsProvider, StockError, StockProvider

router = APIRouter(tags=["stock"])


def get_stock_provider() -> StockProvider | None:
    key = get_settings().pexels_api_key
    return PexelsProvider(key) if key else None


class StockPhotoOut(BaseModel):
    id: str
    thumb_url: str
    width: int
    height: int
    alt: str
    credit: str
    page_url: str


class StockSearchOut(BaseModel):
    enabled: bool
    provider: str = ""
    results: list[StockPhotoOut] = []


class ImportBody(BaseModel):
    photo_id: str = Field(min_length=1, max_length=20, pattern=r"^\d+$")


def _provider_or_503(provider: StockProvider | None) -> StockProvider:
    if provider is None:
        raise HTTPException(503, "Stock photos are not set up on this server")
    return provider


@router.get("/projects/{project_id}/stock/search", response_model=StockSearchOut)
def search_stock(
    q: str = Query("", max_length=100),
    page: int = Query(1, ge=1, le=20),
    access: Access = EDIT_CONTENT,
    provider: StockProvider | None = Depends(get_stock_provider),
):
    if provider is None:
        return StockSearchOut(enabled=False)
    if not q.strip():
        return StockSearchOut(enabled=True, provider=provider.name)
    limit_stock(access.user.id)
    try:
        photos = provider.search(q.strip(), page)
    except StockError as exc:
        raise HTTPException(502, str(exc)) from exc
    keep = {"id", "thumb_url", "width", "height", "alt", "credit", "page_url"}
    return StockSearchOut(
        enabled=True,
        provider=provider.name,
        results=[
            StockPhotoOut(**{k: v for k, v in asdict(p).items() if k in keep}) for p in photos
        ],
    )


@router.post("/projects/{project_id}/stock/import", response_model=AssetOut, status_code=201)
def import_stock(
    body: ImportBody,
    access: Access = EDIT_CONTENT,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
    provider: StockProvider | None = Depends(get_stock_provider),
):
    provider = _provider_or_503(provider)
    limit_stock(access.user.id)
    try:
        photo = provider.get(body.photo_id)
        data = provider.download(photo)
        asset = store_image(
            db,
            storage,
            access,
            data,
            f"{provider.name}-{photo.id}",
            alt=photo.alt,
            credit=photo.credit,
        )
    except StockError as exc:
        raise HTTPException(502, str(exc)) from exc
    except InvalidImage as exc:
        raise HTTPException(422, str(exc)) from exc
    return asset_out(asset)
