"""build(): the one function that turns a document into files."""

from dataclasses import dataclass, field

from sitegen import paths
from sitegen.renderer import AssetFile, Issue, asset_output_path, render_page
from sitegen.schema import SiteDocument


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
    for asset_id, asset in assets.items():
        result.files[asset_output_path(asset_id, asset)] = asset.data
    return result
