"""Editor preview: one page rendered by the same code as the real build (ADR 001)."""

from collections.abc import Callable
from dataclasses import dataclass, field

from sitegen.renderer import AssetFile, Issue, PreviewOptions, render_page
from sitegen.schema import SiteDocument
from sitegen.validate import check


@dataclass
class PreviewResult:
    html: str
    issues: list[Issue] = field(default_factory=list)


def render_preview(
    doc: SiteDocument,
    page_id: str,
    lang: str | None = None,
    asset_url: Callable[[str], str] = lambda asset_id: "",
    assets: dict[str, AssetFile] | None = None,
) -> PreviewResult:
    page = doc.page_by_id(page_id)
    if page is None:
        raise KeyError(page_id)
    lang = lang or doc.site.default_language
    if lang not in doc.site.languages:
        raise KeyError(lang)
    issues = check(doc, assets)
    html = render_page(
        doc, page, lang, assets or {}, issues, preview=PreviewOptions(asset_url=asset_url)
    )
    return PreviewResult(html=html, issues=issues)
