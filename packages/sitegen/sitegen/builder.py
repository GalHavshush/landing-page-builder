"""build(): the one function that turns a document into files."""

from dataclasses import dataclass, field

from sitegen import paths, seo
from sitegen.css import STATIC, compose_css
from sitegen.fonts import font_files
from sitegen.posts import BLOG_DIR, Post
from sitegen.renderer import (
    CSS_PATH,
    JS_PATH,
    SOCIAL_CARD_PATH,
    AssetFile,
    Issue,
    asset_output_path,
    render_not_found,
    render_page,
    render_post,
    variant_output_path,
)
from sitegen.schema import SiteDocument
from sitegen.validate import check


@dataclass
class BuildResult:
    files: dict[str, bytes] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


def build(
    doc: SiteDocument,
    assets: dict[str, AssetFile] | None = None,
    posts: list[Post] | None = None,
    social_card: bytes | None = None,
) -> BuildResult:
    """Build the whole site. `posts` are the published posts (drafts are the caller's to omit).

    `social_card` is a PNG used as the share image wherever no picture was chosen; it is made by
    the caller (see the API) because drawing images needs a library this package avoids.
    """
    assets = assets or {}
    posts = list(posts or [])
    result = BuildResult()
    result.issues += check(doc, assets)
    plan = paths.plan_pages(doc)
    for page in doc.pages:
        for lang in doc.site.languages:
            html = render_page(
                doc, page, lang, assets, result.issues, posts=posts, social_card=bool(social_card)
            )
            result.files[plan[(page.id, lang)]] = html.encode()
    for post in posts:
        if post.lang not in doc.site.languages:
            result.issues.append(
                Issue("warning", f"Post {post.title!r} is in an unknown language {post.lang!r}")
            )
            continue
        html = render_post(doc, post, assets, result.issues, posts, social_card=bool(social_card))
        result.files[paths.post_output_path(doc, post)] = html.encode()
    for lang in doc.site.languages:
        feed = seo.rss_xml(doc, posts, lang)
        if feed:
            prefix = "" if lang == doc.site.default_language else f"{lang}/"
            result.files[f"{prefix}{BLOG_DIR}/feed.xml"] = feed.encode()
    result.files["404.html"] = render_not_found(doc, assets, result.issues).encode()
    result.files["robots.txt"] = seo.robots_txt(doc).encode()
    sitemap = seo.sitemap_xml(doc, posts)
    if sitemap:
        result.files["sitemap.xml"] = sitemap.encode()
    else:
        result.issues.append(
            Issue("warning", "No base_url set: sitemap.xml, canonical and og:image were skipped")
        )
    if social_card:
        result.files[SOCIAL_CARD_PATH] = social_card
    result.files[CSS_PATH] = compose_css(doc).encode()
    result.files[JS_PATH] = (STATIC / "site.js").read_bytes()
    result.files.update(font_files(doc))  # only the fonts and scripts this site uses
    # renderer and validator can report the same problem; show each once
    seen: set[tuple[str, str]] = set()
    result.issues = [
        i
        for i in result.issues
        if (i.level, i.message) not in seen and not seen.add((i.level, i.message))
    ]
    for asset_id, asset in assets.items():
        result.files[asset_output_path(asset_id, asset)] = asset.data
        for width, data in asset.variants:
            result.files[variant_output_path(asset_id, asset, width)] = data
    return result
