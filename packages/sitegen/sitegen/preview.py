"""Editor preview: one page rendered by the same code as the real build (ADR 001)."""

from collections.abc import Callable
from dataclasses import dataclass, field

from sitegen.posts import Post
from sitegen.renderer import AssetFile, Issue, PreviewOptions, render_page, render_post
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
    posts: list[Post] | None = None,
) -> PreviewResult:
    page = doc.page_by_id(page_id)
    if page is None:
        raise KeyError(page_id)
    lang = lang or doc.site.default_language
    if lang not in doc.site.languages:
        raise KeyError(lang)
    issues = check(doc, assets)
    html = render_page(
        doc,
        page,
        lang,
        assets or {},
        issues,
        preview=PreviewOptions(asset_url=asset_url),
        posts=posts,
    )
    return PreviewResult(html=html, issues=issues)


def render_post_preview(
    doc: SiteDocument,
    post: Post,
    asset_url: Callable[[str], str] = lambda asset_id: "",
    assets: dict[str, AssetFile] | None = None,
    all_posts: list[Post] | None = None,
) -> PreviewResult:
    """Preview of one post page (the post may be an unsaved draft)."""
    issues: list[Issue] = []
    if post.lang not in doc.site.languages:
        raise KeyError(post.lang)
    others = [p for p in (all_posts or []) if p.id != post.id]
    html = render_post(
        doc,
        post,
        assets or {},
        issues,
        [*others, post],
        preview=PreviewOptions(asset_url=asset_url),
    )
    return PreviewResult(html=html, issues=issues)
