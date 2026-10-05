"""build(): the one function that turns a document into files."""

from dataclasses import dataclass, field
from pathlib import Path

from sitegen import paths
from sitegen.renderer import (
    CSS_PATH,
    JS_PATH,
    AssetFile,
    Issue,
    asset_output_path,
    render_page,
)
from sitegen.schema import SiteDocument
from sitegen.sections import REGISTRY
from sitegen.theme import theme_css

STATIC = Path(__file__).parent / "static"


@dataclass
class BuildResult:
    files: dict[str, bytes] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


def build(doc: SiteDocument, assets: dict[str, AssetFile] | None = None) -> BuildResult:
    assets = assets or {}
    result = BuildResult()
    plan = paths.plan_pages(doc)
    for page in doc.pages:
        for lang in doc.site.languages:
            html = render_page(doc, page, lang, assets, result.issues)
            result.files[plan[(page.id, lang)]] = html.encode()
    used = {s.type for page in doc.pages for s in page.sections}
    css = [theme_css(doc.theme), (STATIC / "base.css").read_text()]
    css += [REGISTRY[t].css() for t in sorted(used)]  # only CSS for sections actually used
    result.files[CSS_PATH] = "\n".join(c for c in css if c).encode()
    result.files[JS_PATH] = (STATIC / "site.js").read_bytes()
    for asset_id, asset in assets.items():
        result.files[asset_output_path(asset_id, asset)] = asset.data
    return result
