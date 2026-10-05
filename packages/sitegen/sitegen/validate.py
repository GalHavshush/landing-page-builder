"""Semantic checks that go beyond the schema: things that are valid JSON but a bad website.

Everything here is a warning/info, never an exception: users can still preview and export.
"""

from collections.abc import Iterator

from pydantic import BaseModel

from sitegen.fonts import SCRIPT_LABEL, manifest, missing_scripts
from sitegen.models import ImageRef, Link
from sitegen.renderer import AssetFile, Issue
from sitegen.schema import Page, SiteDocument
from sitegen.sections import REGISTRY
from sitegen.theme import contrast_ratio

MIN_CONTRAST = 4.5
# Smallest comfortable picture width (px) for how large it is drawn. Below this it looks soft.
MIN_IMAGE_WIDTH = {"hero": 1200, "gallery": 700, "services": 600, "blog_list": 600}
MIN_IMAGE_WIDTH_DEFAULT = 500
COVER_MIN_WIDTH = 1600  # a full-bleed hero is drawn at the whole screen width


def _walk(value) -> Iterator[BaseModel]:
    if isinstance(value, BaseModel):
        yield value
        for name in type(value).model_fields:
            yield from _walk(getattr(value, name))
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)


def check(doc: SiteDocument, assets: dict[str, AssetFile] | None = None) -> list[Issue]:
    assets = assets or {}
    issues: list[Issue] = []
    page_ids = {p.id for p in doc.pages}

    palette = doc.theme.palette
    for fg, bg in (("text", "background"), ("text", "surface")):
        ratio = contrast_ratio(palette[fg], palette[bg])
        if ratio < MIN_CONTRAST:
            issues.append(
                Issue(
                    "warning", f"Low contrast between {fg} and {bg} colors ({ratio:.1f}:1)", "theme"
                )
            )

    for key, script in missing_scripts(doc):
        issues.append(
            Issue(
                "warning",
                f"{manifest()[key]['family']} has no {SCRIPT_LABEL.get(script, script)} letters; "
                "visitors will see a fallback font for that language",
                "theme",
            )
        )
    if doc.site.logo and not doc.site.logo.alt.strip():
        issues.append(Issue("warning", "The logo has no alt text (use the business name)", "site"))
    if doc.site.header.transparent and not any(
        p.sections and p.sections[0].type == "hero" and p.sections[0].variant == "cover"
        for p in doc.pages
    ):
        issues.append(
            Issue(
                "info",
                "The transparent header only shows over a Cover hero at the top of a page",
                "site",
            )
        )
    if not doc.pages:
        issues.append(Issue("warning", "The site has no pages", "site"))
    for page in doc.pages:
        issues += _check_page(doc, page, page_ids, assets)
    for lang in doc.site.languages:
        if lang != doc.site.default_language and lang not in doc.site.i18n:
            issues.append(Issue("info", f"No {lang} translation of site name/footer", "site"))
    return issues


def _check_page(doc, page: Page, page_ids: set[str], assets) -> list[Issue]:
    issues: list[Issue] = []
    where = f"page {page.title!r}"
    if not page.sections:
        issues.append(Issue("warning", "Page has no sections", where))
    if not (page.seo.description or doc.site.seo.default_description):
        issues.append(Issue("info", "No meta description", where))
    for section in page.sections:
        sec_where = f"{where} / {REGISTRY[section.type].label} ({section.id})"
        for node in _walk(section.props):
            if isinstance(node, ImageRef):
                if node.asset not in assets and assets is not None and assets:
                    issues.append(Issue("warning", f"Missing image {node.asset!r}", sec_where))
                if not node.alt.strip():
                    issues.append(Issue("warning", "Image has no alt text", sec_where))
                file = assets.get(node.asset) if assets else None
                if file and file.width:
                    need = MIN_IMAGE_WIDTH.get(section.type, MIN_IMAGE_WIDTH_DEFAULT)
                    if section.type == "hero" and section.variant in ("cover", "banner"):
                        need = COVER_MIN_WIDTH
                    if file.width < need:
                        issues.append(
                            Issue(
                                "warning",
                                f"This image is only {file.width}px wide; it may look blurry here "
                                f"(try one at least {need}px wide)",
                                sec_where,
                            )
                        )
            if isinstance(node, Link):
                if node.page is not None and node.page not in page_ids:
                    issues.append(
                        Issue("warning", f"Link to unknown page {node.page!r}", sec_where)
                    )
        for lang in doc.site.languages:
            if lang == doc.site.default_language:
                continue
            override = section.i18n.get(lang, {})
            missing = sorted(
                f
                for f in REGISTRY[section.type].translatable
                if getattr(section.props, f) and f not in override
            )
            if missing:
                issues.append(
                    Issue("info", f"Not translated to {lang}: {', '.join(missing)}", sec_where)
                )
    return issues
