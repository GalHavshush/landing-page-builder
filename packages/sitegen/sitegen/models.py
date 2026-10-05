"""Building blocks shared by the site document and every section type.

Design rules (see docs/adr/002):
- every model forbids unknown keys, so typos fail loudly;
- every option is an enum (Literal), never a free CSS value;
- links are structured, and only safe URL schemes are allowed.
"""

import re
import uuid
from functools import partial
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def field(group: str, control: str, default: Any = ..., *, default_factory=None, **extra):
    """Declare a prop field with editor metadata.

    group:   "content" (what a client may edit, and what can be translated) or
             "design" (layout/appearance, designers only).
    control: which input the properties panel renders (text, textarea, richtext, image, ...).
    """
    meta = {"group": group, "control": control, **extra}
    if default_factory is not None:
        return Field(default_factory=default_factory, json_schema_extra=meta)
    return Field(default, json_schema_extra=meta)


content = partial(field, "content")
design = partial(field, "design")

_SAFE_URL = re.compile(r"^(https?://|mailto:|tel:|#)", re.IGNORECASE)


class Link(Strict):
    """A link to a page of this site, an external URL, or an uploaded asset (exactly one)."""

    page: str | None = None
    url: str | None = None
    asset: str | None = None

    @model_validator(mode="after")
    def _exactly_one(self):
        if sum(v is not None for v in (self.page, self.url, self.asset)) != 1:
            raise ValueError("a link needs exactly one of: page, url, asset")
        if self.url is not None and not _SAFE_URL.match(self.url.strip()):
            raise ValueError("url must start with http://, https://, mailto:, tel: or #")
        return self


class ImageRef(Strict):
    asset: str
    alt: str = ""


class Button(Strict):
    label: str
    href: Link
    style: Literal["primary", "secondary", "outline", "link"] = "primary"


class SectionStyle(Strict):
    """Design options every section has. All enums."""

    background: Literal["default", "alt", "primary", "dark"] = "default"
    spacing: Literal["compact", "normal", "spacious"] = "normal"
    align: Literal["start", "center", "end"] = "start"


class BaseSection(Strict):
    """Fields common to every section. Concrete sections add `type`, `variant` and `props`.

    `i18n` maps language -> {prop name: translated value}; only content-group props may be
    translated, and missing values fall back to the default language (docs/adr/006).
    """

    id: str = Field(default_factory=lambda: new_id("sec"))
    style: SectionStyle = Field(default_factory=SectionStyle)
    i18n: dict[str, dict[str, Any]] = Field(default_factory=dict)


def fields_in_group(props_model: type[BaseModel], group: str) -> set[str]:
    return {
        name
        for name, info in props_model.model_fields.items()
        if (info.json_schema_extra or {}).get("group") == group
    }
