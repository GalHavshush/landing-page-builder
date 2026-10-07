from datetime import datetime

from pydantic import BaseModel, Field
from sitegen.brief import Brief


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    template: str = "clean"
    language: str = "en"  # the site's main language
    extra_languages: list[str] = Field(default_factory=list)  # offered in addition to it


class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectOut(BaseModel):
    id: int
    name: str
    slug: str
    template_id: str
    role: str
    revision: int
    updated_at: datetime


class DocOut(BaseModel):
    doc: dict
    revision: int


class DocIn(BaseModel):
    doc: dict
    base_revision: int  # the revision this edit was based on


class SavedOut(BaseModel):
    revision: int
    warnings: list[dict] = []


class PreviewIn(BaseModel):
    doc: dict
    page_id: str
    lang: str | None = None
    interactive: bool = False  # a try-it-out preview instead of the click-to-select one


class BriefPreviewIn(BaseModel):
    brief: Brief
    page_id: str | None = None  # default: the home page


class PreviewOut(BaseModel):
    html: str
    issues: list[dict] = []
