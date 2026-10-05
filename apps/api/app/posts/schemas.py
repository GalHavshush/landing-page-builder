import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PostIn(BaseModel):
    lang: str
    title: str = Field(min_length=1, max_length=300)
    slug: str = Field(min_length=1, max_length=120)
    excerpt: str = Field(default="", max_length=600)
    body_md: str = Field(default="", max_length=200_000)
    cover_asset_id: str | None = None
    status: Literal["draft", "published"] = "draft"
    published_at: datetime | None = None

    @field_validator("slug")
    @classmethod
    def _slug(cls, v: str) -> str:
        if not _SLUG.match(v):
            raise ValueError("use lowercase letters, numbers and single hyphens")
        return v


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lang: str
    translation_group: str
    title: str
    slug: str
    excerpt: str
    body_md: str
    cover_asset_id: str | None
    status: str
    published_at: datetime | None
    updated_at: datetime


class TranslateIn(BaseModel):
    lang: str


class PostPreviewIn(PostIn):
    pass
