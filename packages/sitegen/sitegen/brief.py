"""The guided new-site form: answers (a Brief) in, a ready-to-edit site document out.

`build_document` starts from a starter (theme, fonts, header/footer look, hero), localizes it, and
fills it with what the owner typed. Anything left blank keeps the starter's placeholder text for
core sections, and optional sections (stats, testimonials, ...) are left out rather than filled
with made-up claims. Pure: no web or DB imports.
"""

import re
from typing import Literal

from pydantic import Field, field_validator

from sitegen.localize import translate
from sitegen.models import Strict
from sitegen.schema import Business, SiteDocument
from sitegen.sections import create_section
from sitegen.starters import load_starter

BusinessType = Literal[
    "general",
    "local_shop",
    "restaurant",
    "salon",
    "trades",
    "clinic",
    "photographer",
    "consultant",
    "fitness",
    "garden",
    "portfolio",
]
STARTER_FOR_TYPE: dict[str, str] = {
    "general": "clean",
    "local_shop": "warm",
    "restaurant": "restaurant",
    "salon": "salon",
    "trades": "trades",
    "clinic": "clinic",
    "photographer": "photographer",
    "consultant": "consultant",
    "fitness": "gym",
    "garden": "landscaping",
    "portfolio": "minimal",
}
PageKind = Literal["about", "services", "pricing", "team", "faq"]
PAGE_ORDER: tuple[str, ...] = ("about", "services", "pricing", "team", "faq")
PAGE_TITLE = {
    "about": "About",
    "services": "Services",
    "pricing": "Pricing",
    "team": "Team",
    "faq": "FAQ",
}
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

# Text the generator writes itself (goal buttons); languages without an entry get English.
GOAL_LABEL = {
    "call": {"en": "Call us", "he": "התקשרו אלינו"},
    "book": {"en": "Book now", "he": "לקביעת תור"},
    "message": {"en": "Get in touch", "he": "צרו קשר"},
    "visit": {"en": "Visit us", "he": "בואו לבקר"},
}


class Goal(Strict):
    """The one thing a visitor should do: becomes the main button on the home page and header."""

    kind: Literal["call", "book", "message", "visit"] = "message"
    url: str = ""  # "book": an external booking link (https://...)


class Highlight(Strict):
    title: str = ""
    text: str = ""


class StatItem(Strict):
    value: str = ""
    label: str = ""


class ServiceItem(Strict):
    title: str = ""
    description: str = ""
    price: str = ""


class PlanItem(Strict):
    name: str = ""
    price: str = ""
    period: str = ""
    features: str = ""  # one per line
    highlighted: bool = False


class MemberItem(Strict):
    name: str = ""
    role: str = ""
    bio: str = ""


class FaqEntry(Strict):
    question: str = ""
    answer: str = ""


class QuoteItem(Strict):
    quote: str = ""
    author: str = ""
    role: str = ""


class BriefPalette(Strict):
    primary: str | None = None
    accent: str | None = None

    @field_validator("primary", "accent")
    @classmethod
    def _hex(cls, v: str | None) -> str | None:
        if v is not None and not _HEX.match(v):
            raise ValueError("colors must be #RRGGBB")
        return v


class Brief(Strict):
    name: str = Field(min_length=1, max_length=200)
    language: str = "en"
    extra_languages: list[str] = Field(default_factory=list)
    business_type: BusinessType = "general"
    template: str | None = None  # a starter chosen on the "look" step; overrides the business type
    tagline: str = ""
    description: str = ""
    goal: Goal = Field(default_factory=Goal)
    business: Business = Field(default_factory=Business)
    pages: list[PageKind] = Field(default_factory=list)
    palette: BriefPalette = Field(default_factory=BriefPalette)
    # home page
    headline: str = ""
    subheading: str = ""
    highlights: list[Highlight] = Field(default_factory=list)
    stats: list[StatItem] = Field(default_factory=list)
    testimonials: list[QuoteItem] = Field(default_factory=list)
    # other pages
    story: str = ""
    services: list[ServiceItem] = Field(default_factory=list)
    plans: list[PlanItem] = Field(default_factory=list)
    team: list[MemberItem] = Field(default_factory=list)
    faq: list[FaqEntry] = Field(default_factory=list)


def _filled(items) -> list[dict]:
    """Items as dicts, minus the ones the owner left completely blank."""
    out = []
    for item in items:
        data = item.model_dump(mode="json")
        if any(isinstance(v, str) and v.strip() for v in data.values()):
            out.append(data)
    return out


class _Builder:
    def __init__(self, brief: Brief):
        self.brief = brief
        self.lang = brief.language

    def tr(self, text: str) -> str:
        return translate({"label": text}, self.lang)["label"]

    def section(
        self, type_: str, variant: str | None = None, background: str | None = None, **props
    ):
        s = translate(create_section(type_).model_dump(mode="json"), self.lang)
        if variant:
            s["variant"] = variant
        if background:
            s["style"]["background"] = background
        s["props"].update({k: v for k, v in props.items() if v not in ("", [], None)})
        return s

    def button(self, contact_id: str) -> dict:
        goal, phone = self.brief.goal, self.brief.business.phone.strip()
        kind = goal.kind
        if kind == "call" and not phone:
            kind = "message"
        if kind == "book" and not goal.url.strip():
            kind = "message"
        if kind == "call":
            href = {"url": "tel:" + re.sub(r"[^\d+]", "", phone)}
        elif kind == "book":
            href = {"url": goal.url.strip()}
        else:
            href = {"page": contact_id}
        label = GOAL_LABEL[kind].get(self.lang, GOAL_LABEL[kind]["en"])
        return {"label": label, "href": {"page": None, "url": None, "asset": None, **href}}

    def cta(self, button: dict) -> dict:
        return self.section("cta", "banner", "primary", buttons=[button])

    def page(self, page_id: str, slug: str, title: str, sections: list[dict]) -> dict:
        return {
            "id": page_id,
            "slug": slug,
            "title": self.tr(title),
            "sections": sections,
            "i18n": {},
        }

    def home(self, starter_home: dict, button: dict) -> dict:
        b = self.brief
        hero = next((s for s in starter_home["sections"] if s["type"] == "hero"), None)
        hero = hero or self.section("hero", "centered")
        props = hero["props"]
        props["heading"] = b.headline.strip() or b.tagline.strip() or props["heading"]
        props["subheading"] = b.subheading.strip() or b.description.strip() or props["subheading"]
        props["buttons"] = [button]
        sections = [hero]
        highlights = _filled(b.highlights)
        if highlights:
            sections.append(
                self.section("features", "cards", items=[{"icon": None, **h} for h in highlights])
            )
        stats = _filled(b.stats)
        if stats:
            sections.append(self.section("stats", "row", "alt", items=stats))
        quotes = _filled(b.testimonials)
        if quotes:
            sections.append(self.section("testimonials", "cards", items=quotes))
        sections.append(self.cta(button))
        return self.page("pg_home", "", "Home", sections)

    def other(self, kind: str, button: dict) -> dict:
        b = self.brief
        if kind == "about":
            body = [self.section("text", "split", body=b.story.strip())]
        elif kind == "services":
            body = [self.section("services", "cards", items=_filled(b.services))]
        elif kind == "pricing":
            body = [self.section("pricing", "cards", plans=_filled(b.plans))]
        elif kind == "team":
            body = [self.section("team", "cards", items=_filled(b.team))]
        else:
            body = [self.section("faq", "accordion", items=_filled(b.faq))]
        return self.page(f"pg_{kind}", kind, PAGE_TITLE[kind], [*body, self.cta(button)])

    def contact(self) -> dict:
        sections = [
            self.section("contact", "split"),
            self.section("hours", "card", "alt", show_contact=False),
        ]
        if self.brief.business.address.strip():
            sections.append(self.section("map", "embedded"))
        return self.page("pg_contact", "contact", "Contact", sections)


def build_document(brief: Brief) -> SiteDocument:
    """The site described by `brief`, as a document the editor can open."""
    template = brief.template or STARTER_FOR_TYPE[brief.business_type]
    data = load_starter(template, lang=brief.language).model_dump(mode="json")
    builder = _Builder(brief)
    button = builder.button("pg_contact")
    chosen = [k for k in PAGE_ORDER if k in brief.pages]
    pages = [
        builder.home(data["pages"][0], button),
        *(builder.other(k, button) for k in chosen),
        builder.contact(),
    ]
    languages = list(dict.fromkeys([brief.language, *brief.extra_languages]))
    description = brief.description.strip() or brief.tagline.strip()
    site = data["site"]
    site.update(
        name=brief.name.strip(),
        tagline=brief.tagline.strip(),
        default_language=languages[0],
        languages=languages,
        business=brief.business.model_dump(mode="json"),
        nav=[{"label": p["title"], "page": p["id"], "labels": {}} for p in pages],
    )
    site["seo"] = {**site["seo"], "default_description": description}
    site["header"] = {**site["header"], "cta": button}
    site["i18n"] = {}
    theme = data["theme"]
    theme["palette"] = {
        **theme["palette"],
        **{k: v for k, v in brief.palette.model_dump().items() if v},
    }
    return SiteDocument.model_validate({**data, "site": site, "theme": theme, "pages": pages})
