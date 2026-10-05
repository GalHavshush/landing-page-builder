"""The website document: the single JSON structure that describes a whole site (ADR 002)."""

import re
from typing import Literal

from pydantic import Field, field_validator, model_validator

from sitegen.models import Button, ImageRef, Link, Strict, new_id
from sitegen.sections import REGISTRY, Section

SCHEMA_VERSION = 1
FontName = Literal[
    "sans",
    "serif",
    "humanist",
    "rounded",  # system stacks: no files, instant
    "dm-sans",
    "manrope",
    "plus-jakarta",
    "fraunces",
    "source-serif",
    "heebo",
    "rubik",  # bundled web fonts (fonts.py)
]
_LANG = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})?$")
_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RTL_LANGUAGES = {"ar", "he", "fa", "ur", "yi", "ps", "sd", "ckb", "dv"}


def language_dir(lang: str) -> str:
    return "rtl" if lang.split("-")[0] in RTL_LANGUAGES else "ltr"


class SEO(Strict):
    title: str | None = None
    description: str | None = None
    social_image: str | None = None  # asset id
    noindex: bool = False


class Hours(Strict):
    label: str  # e.g. "Mon-Fri"
    open: str = ""
    close: str = ""
    closed: bool = False


class Business(Strict):
    """Shared business info. Sections (contact, footer, map) read from here."""

    phone: str = ""
    email: str = ""
    address: str = ""
    hours: list[Hours] = Field(default_factory=list)
    social: dict[str, str] = Field(default_factory=dict)


class SiteSEO(Strict):
    title_template: str = "{page} | {site}"
    default_description: str = ""
    social_image: str | None = None


class NavItem(Strict):
    label: str
    page: str  # page id
    labels: dict[str, str] = Field(default_factory=dict)  # translations


class Footer(Strict):
    text: str = ""
    show_business_info: bool = True
    style: Literal["columns", "centered", "minimal"] = "columns"


class Header(Strict):
    """Top-of-page navigation bar."""

    style: Literal["classic", "centered", "split"] = "classic"
    sticky: bool = True
    # Sits over a full-width cover hero at the top of a page and turns solid once you scroll.
    transparent: bool = False
    cta: Button | None = None  # an optional call-to-action button in the bar


class Announcement(Strict):
    """A slim banner above the header: a sale, new opening hours, a booking deadline."""

    enabled: bool = False
    text: str = ""
    link: Link | None = None


class SiteTranslation(Strict):
    name: str | None = None
    tagline: str | None = None
    description: str | None = None
    address: str | None = None
    hours: list[Hours] | None = None
    footer_text: str | None = None
    cta_label: str | None = None
    announcement_text: str | None = None


class Site(Strict):
    name: str
    tagline: str = ""
    default_language: str = "en"
    languages: list[str] = Field(default_factory=lambda: ["en"])
    base_url: str = ""
    business: Business = Field(default_factory=Business)
    seo: SiteSEO = Field(default_factory=SiteSEO)
    nav: list[NavItem] = Field(default_factory=list)
    footer: Footer = Field(default_factory=Footer)
    logo: ImageRef | None = None  # shown instead of the site name in the header; alt = the name
    logo_size: Literal["small", "medium", "large"] = "medium"
    header: Header = Field(default_factory=Header)
    announcement: Announcement = Field(default_factory=Announcement)
    i18n: dict[str, SiteTranslation] = Field(default_factory=dict)

    @field_validator("base_url")
    @classmethod
    def _base_url(cls, v: str) -> str:
        v = v.strip().rstrip("/")
        if v and not re.match(r"^https?://", v):
            raise ValueError("base_url must start with http:// or https://")
        return v

    @field_validator("languages")
    @classmethod
    def _languages(cls, v: list[str]) -> list[str]:
        if not v or len(set(v)) != len(v):
            raise ValueError("languages must be a non-empty list without duplicates")
        for code in v:
            if not _LANG.match(code):
                raise ValueError(f"invalid language code: {code!r}")
        return v


class Theme(Strict):
    template: str = "clean"
    palette: dict[str, str] = Field(
        default_factory=lambda: {
            "primary": "#2563EB",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "surface": "#F3F4F6",
            "text": "#111827",
        }
    )
    fonts: dict[Literal["heading", "body"], FontName] = Field(
        default_factory=lambda: {"heading": "sans", "body": "sans"}
    )
    radius: Literal["none", "sm", "md", "lg", "full"] = "md"
    button_style: Literal["solid", "outline", "soft"] = "solid"
    spacing: Literal["compact", "normal", "spacious"] = "normal"
    card_style: Literal["outlined", "flat", "elevated"] = "outlined"
    image_style: Literal["rounded", "square", "soft"] = "rounded"
    heading_style: Literal["tight", "caps", "light"] = "tight"
    motion: Literal["none", "subtle", "lively"] = "subtle"

    @field_validator("palette")
    @classmethod
    def _palette(cls, v: dict[str, str]) -> dict[str, str]:
        required = {"primary", "accent", "background", "surface", "text"}
        if set(v) != required:
            raise ValueError(f"palette must define exactly: {sorted(required)}")
        for name, value in v.items():
            if not re.match(r"^#[0-9a-fA-F]{6}$", value):
                raise ValueError(f"palette.{name} must be a #RRGGBB color")
        return v


class PageTranslation(Strict):
    title: str | None = None
    slug: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None


class Page(Strict):
    id: str = Field(default_factory=lambda: new_id("pg"))
    slug: str = ""  # "" is the home page
    title: str
    seo: SEO = Field(default_factory=SEO)
    sections: list[Section] = Field(default_factory=list)
    i18n: dict[str, PageTranslation] = Field(default_factory=dict)

    @field_validator("slug")
    @classmethod
    def _slug(cls, v: str) -> str:
        if v and not _SLUG.match(v):
            raise ValueError("slug must be lowercase letters, digits and single hyphens")
        return v


class SiteDocument(Strict):
    schema_version: int = SCHEMA_VERSION
    site: Site
    theme: Theme = Field(default_factory=Theme)
    pages: list[Page] = Field(default_factory=list)

    def page_slug(self, page: Page, lang: str) -> str:
        tr = page.i18n.get(lang)
        return tr.slug if tr and tr.slug is not None else page.slug

    def page_by_id(self, page_id: str) -> Page | None:
        return next((p for p in self.pages if p.id == page_id), None)

    @model_validator(mode="after")
    def _consistency(self):
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version {self.schema_version}")
        site = self.site
        if site.default_language not in site.languages:
            raise ValueError("default_language must be one of languages")
        others = set(site.languages) - {site.default_language}

        def check_langs(owner: str, keys) -> None:
            bad = set(keys) - others
            if bad:
                raise ValueError(f"{owner}: i18n has unknown or default languages {sorted(bad)}")

        check_langs("site", site.i18n)
        ids: set[str] = set()
        for page in self.pages:
            check_langs(f"page {page.id}", page.i18n)
            for sec in [page, *page.sections]:
                if sec.id in ids:
                    raise ValueError(f"duplicate id {sec.id!r}")
                ids.add(sec.id)
            for sec in page.sections:
                check_langs(f"section {sec.id}", sec.i18n)
                definition = REGISTRY[sec.type]
                for override in sec.i18n.values():
                    illegal = set(override) - definition.translatable
                    if illegal:
                        raise ValueError(
                            f"section {sec.id}: {sorted(illegal)} are not translatable fields"
                        )
                    # values must be valid for the prop they replace
                    definition.props_model.model_validate({**sec.props.model_dump(), **override})
        for lang in site.languages:
            slugs = [self.page_slug(p, lang) for p in self.pages]
            if len(set(slugs)) != len(slugs):
                raise ValueError(f"duplicate page slugs for language {lang!r}")
        for item in site.nav:
            if item.page not in {p.id for p in self.pages}:
                raise ValueError(f"nav item {item.label!r} points to unknown page {item.page!r}")
            check_langs(f"nav {item.label!r}", item.labels)
        return self
