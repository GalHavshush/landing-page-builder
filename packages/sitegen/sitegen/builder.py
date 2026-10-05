"""build(): the one function that turns a document into files."""

from dataclasses import dataclass, field

from sitegen import paths, seo
from sitegen.css import STATIC, compose_css
from sitegen.renderer import (
    CSS_PATH,
    JS_PATH,
    AssetFile,
    Issue,
    asset_output_path,
    render_not_found,
    render_page,
)
from sitegen.schema import SiteDocument
from sitegen.validate import check


@dataclass
class BuildResult:
    files: dict[str, bytes] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


def build(doc: SiteDocument, assets: dict[str, AssetFile] | None = None) -> BuildResult:
    assets = assets or {}
    result = BuildResult()
    result.issues += check(doc, assets)
    plan = paths.plan_pages(doc)
    for page in doc.pages:
        for lang in doc.site.languages:
            html = render_page(doc, page, lang, assets, result.issues)
            result.files[plan[(page.id, lang)]] = html.encode()
    result.files["404.html"] = render_not_found(doc, assets, result.issues).encode()
    result.files["robots.txt"] = seo.robots_txt(doc).encode()
    sitemap = seo.sitemap_xml(doc)
    if sitemap:
        result.files["sitemap.xml"] = sitemap.encode()
    else:
        result.issues.append(
            Issue("warning", "No base_url set: sitemap.xml, canonical and og:image were skipped")
        )
    result.files[CSS_PATH] = compose_css(doc).encode()
    result.files[JS_PATH] = (STATIC / "site.js").read_bytes()
    # renderer and validator can report the same problem; show each once
    seen: set[tuple[str, str]] = set()
    result.issues = [
        i
        for i in result.issues
        if (i.level, i.message) not in seen and not seen.add((i.level, i.message))
    ]
    for asset_id, asset in assets.items():
        result.files[asset_output_path(asset_id, asset)] = asset.data
    return result
