"""Turns a SiteDocument + one page + one language into an HTML string."""

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from sitegen import jsonld, paths, seo, strings
from sitegen.css import STATIC, compose_css
from sitegen.icons import render_icon
from sitegen.markdown import render_markdown
from sitegen.models import Button, ImageRef, Link
from sitegen.posts import Post, format_date, sort_newest_first
from sitegen.schema import SEO, Page, SiteDocument, language_dir
from sitegen.sections import REGISTRY
from sitegen.sections.base import SECTIONS_DIR
from sitegen.theme import readable_on
from sitegen.youtube import youtube_id

TEMPLATES_DIR = Path(__file__).parent / "templates"
CSS_PATH = "css/site.css"
JS_PATH = "js/site.js"


@dataclass
class AssetFile:
    """An uploaded file as the generator sees it. Storage/processing happen elsewhere."""

    filename: str
    data: bytes
    mime: str = "application/octet-stream"
    width: int | None = None
    height: int | None = None
    # smaller copies of the same picture: [(width, data)], for srcset. `data` is the largest.
    variants: list[tuple[int, bytes]] = field(default_factory=list)
    color: str | None = None  # average colour, shown while the image loads


@dataclass
class PreviewOptions:
    """Editor preview mode: inline CSS, no navigation, and section ids for click-to-select."""

    asset_url: Callable[[str], str]  # asset id -> URL the editor's iframe can load
    font_base: str = "/fonts/"  # where the editor's iframe can load bundled fonts from
    # A try-it-out preview: no click-to-select markup, so animations, the gallery lightbox and the
    # menu behave as on the real site; internal links report the page they lead to.
    interactive: bool = False


@dataclass
class Issue:
    level: str  # "error" | "warning"
    message: str
    where: str = ""


def fit_cols(columns: int, count: int) -> int:
    """Columns that suit `count` items: no empty columns, and 4 items sit as a tidy 2x2."""
    if count <= 1:
        return 1
    if count == 4 and columns == 3:
        return 2
    return min(columns, count)


@lru_cache(maxsize=1)
def get_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader([str(TEMPLATES_DIR), str(SECTIONS_DIR)]),
        autoescape=True,  # every template is HTML
        undefined=StrictUndefined,
        lstrip_blocks=True,
    )
    env.globals["fit_cols"] = fit_cols
    return env


def _empty_hint(section, lang: str, doc) -> str | None:
    from sitegen.sections import empty_hint

    return empty_hint(section.type, localized_props(section, lang, doc.site.default_language))


def localized_props(section, lang: str, default_lang: str):
    """Section props for `lang`: translated values override, anything missing falls back."""
    override = section.i18n.get(lang) if lang != default_lang else None
    if not override:
        return section.props
    return REGISTRY[section.type].props_model.model_validate(
        {**section.props.model_dump(), **override}
    )


class RenderContext:
    """Per-page helpers exposed to templates as `ctx`."""

    def __init__(
        self,
        doc: SiteDocument,
        lang: str,
        out_path: str,
        assets,
        issues: list[Issue],
        absolute: bool = False,
        page_id: str | None = None,
        preview: PreviewOptions | None = None,
        posts: list[Post] | None = None,
        social_card: bool = False,
    ):
        self.social_card = social_card  # a generated share image exists at SOCIAL_CARD_PATH
        self.doc = doc
        self.posts = posts or []
        self.lang = lang
        self.out_path = out_path
        self.assets = assets
        self.issues = issues
        self.plan = paths.plan_pages(doc)
        self.page_id = page_id
        self.preview = preview
        self.absolute = absolute  # root-relative URLs (needed for 404.html, served at any depth)

    @property
    def editing(self) -> bool:
        """Editor preview with click-to-select (not a real build or an interactive preview)."""
        return self.preview is not None and not self.preview.interactive

    def rel(self, target: str) -> str:
        if self.preview:
            # "#pg:<page id>:<lang>" lets the editor switch to that page; "#" if it is not a page
            for (page_id, lang), path in self.plan.items():
                if path == target:
                    return f"#pg:{page_id}:{lang}"
            return "#"
        return "/" + target if self.absolute else paths.relative(self.out_path, target)

    def asset_path(self, asset_id: str) -> str | None:
        asset = self.assets.get(asset_id)
        return asset_output_path(asset_id, asset) if asset else None

    def link(self, link: Link | None) -> str:
        if link is None:
            return "#"
        if link.url is not None:
            return link.url
        if link.page is not None:
            target = self.plan.get((link.page, self.lang))
            if target is None:
                self.issues.append(Issue("warning", f"link to unknown page {link.page!r}"))
                return "#"
            return self.rel(target)
        if self.preview:
            return self.preview.asset_url(link.asset)
        path = self.asset_path(link.asset)
        if path is None:
            self.issues.append(Issue("warning", f"link to missing asset {link.asset!r}"))
            return "#"
        return self.rel(path)

    def image(self, ref: ImageRef | None) -> dict | None:
        if ref is None:
            return None
        asset = self.assets.get(ref.asset)
        if asset is None and not self.preview:
            self.issues.append(Issue("warning", f"missing image asset {ref.asset!r}"))
            return None
        srcset = ""
        if self.preview:
            src = self.preview.asset_url(ref.asset)
        else:
            src = self.rel(self.asset_path(ref.asset))
            if asset.variants:
                parts = [
                    f"{self.rel(variant_output_path(ref.asset, asset, w))} {w}w"
                    for w, _ in sorted(asset.variants)
                ]
                parts.append(f"{src} {asset.width}w")
                srcset = ", ".join(parts)
        style = []
        if asset and asset.color:
            style.append(f"background-color:{asset.color}")
        if (ref.focus.x, ref.focus.y) != (50, 50):
            style.append(f"object-position:{ref.focus.x}% {ref.focus.y}%")
        return {
            "src": src,
            "srcset": srcset,
            "alt": ref.alt,
            "width": asset.width if asset else None,
            "height": asset.height if asset else None,
            "style": ";".join(style),
        }

    def site_view(self) -> dict:
        """Site-level text for this language (translations override, defaults fall back)."""
        site = self.doc.site
        tr = site.i18n.get(self.lang) if self.lang != site.default_language else None

        def pick(name: str, fallback):
            value = getattr(tr, name, None) if tr else None
            return fallback if value is None else value

        return {
            "name": pick("name", site.name),
            "tagline": pick("tagline", site.tagline),
            "description": pick("description", site.seo.default_description),
            "phone": site.business.phone,
            "email": site.business.email,
            "social": [
                {"label": k.strip().title(), "href": u}
                for k, u in site.business.social.items()
                if u.split("//", 1)[1]  # skip a bare "https://" left in the editor
            ],
            "address": pick("address", site.business.address),
            "hours": pick("hours", site.business.hours),
            "footer_text": pick("footer_text", site.footer.text),
            "cta_label": pick("cta_label", site.header.cta.label if site.header.cta else ""),
            "announcement_text": pick("announcement_text", site.announcement.text),
        }

    def nav(self) -> list[dict]:
        items = []
        for item in self.doc.site.nav:
            target = self.plan.get((item.page, self.lang))
            if target is None:
                continue
            items.append(
                {
                    "label": item.labels.get(self.lang, item.label),
                    "href": self.rel(target),
                    "current": target == self.out_path,
                    "page_id": item.page,  # the editor preview uses it to jump to that page
                }
            )
        return items

    def icon(self, name: str | None) -> Markup:
        return render_icon(name)

    def t(self, key: str) -> str:
        return strings.get(self.lang, key)

    def language_links(self) -> list[dict]:
        """Links to this same page in every language (empty for single-language sites)."""
        if len(self.doc.site.languages) < 2 or self.page_id is None:
            return []
        links = []
        for code in self.doc.site.languages:
            target = self.plan[(self.page_id, code)]
            links.append(
                {
                    "code": code,
                    "label": strings.language_name(code),
                    "href": self.rel(target),
                    "current": code == self.lang,
                }
            )
        return links

    def youtube_id(self, url: str) -> str | None:
        vid = youtube_id(url)
        if vid is None and url.strip():
            self.issues.append(Issue("warning", f"Could not read this YouTube link: {url!r}"))
        return vid

    def blog_posts(self, limit: int = 0) -> list[dict]:
        """Published posts in this language, newest first, ready for templates."""
        posts = sort_newest_first([p for p in self.posts if p.lang == self.lang])
        if limit:
            posts = posts[:limit]
        return [self.post_view(p) for p in posts]

    def post_view(self, post: Post) -> dict:
        cover = self.image(ImageRef(asset=post.cover)) if post.cover else None
        return {
            "title": post.title,
            "excerpt": post.excerpt,
            "href": self.rel(paths.post_output_path(self.doc, post)),
            "cover": cover,
            "date": format_date(post.published_at, self.lang),
            "iso_date": post.published_at.date().isoformat(),
        }

    def header_view(self, first_section) -> dict:
        """Everything the header/announcement markup needs, resolved for this page and language."""
        site = self.doc.site
        view = self.site_view()
        cta = site.header.cta
        cover = bool(
            first_section and first_section.type == "hero" and first_section.variant == "cover"
        )
        # a light tint over the picture needs dark header text; everything else needs light text
        light_overlay = cover and first_section.props.overlay == "light"
        return {
            "style": site.header.style,
            "sticky": site.header.sticky,
            "overlay": site.header.transparent and cover,
            "tone": "dark" if light_overlay else "light",
            "logo": self.image(site.logo) if site.logo else None,
            "logo_size": site.logo_size,
            "cta": {"label": view["cta_label"], "href": self.link(cta.href), "style": cta.style}
            if cta and view["cta_label"]
            else None,
            "announcement": {
                "text": view["announcement_text"],
                "href": self.link(site.announcement.link) if site.announcement.link else None,
            }
            if site.announcement.enabled and view["announcement_text"]
            else None,
        }

    def md(self, source: str) -> Markup:
        """Markdown -> safe HTML. `asset:<id>` links/images resolve to uploaded files."""

        def resolve(match):
            asset_id = match.group(1)
            if self.preview:
                return self.preview.asset_url(asset_id)
            path = self.asset_path(asset_id)
            if path is None:
                self.issues.append(Issue("warning", f"missing asset {asset_id!r} in text"))
                return "#"
            return self.rel(path)

        source = re.sub(r"asset:(asset_[0-9a-f]+)", resolve, source or "")
        return Markup(render_markdown(source))  # noqa: S704 - sanitised by nh3


def variant_output_path(asset_id: str, asset: AssetFile, width: int) -> str:
    stem, dot, ext = asset_output_path(asset_id, asset).rpartition(".")
    return f"{stem}-{width}w{dot}{ext}"


def asset_output_path(asset_id: str, asset: AssetFile) -> str:
    digest = hashlib.sha256(asset.data).hexdigest()[:8]
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", asset.filename).strip("-") or "file"
    return f"assets/{digest}-{name}"


def _render_layout(
    doc: SiteDocument,
    lang: str,
    ctx: RenderContext,
    sections_html: list[str],
    head: dict,
    preview: PreviewOptions | None,
    languages: list[dict],
    first_section=None,
) -> str:
    plan = ctx.plan
    home = plan[(doc.pages[0].id, lang)] if doc.pages else ctx.out_path
    return (
        get_env()
        .get_template("layout.html.j2")
        .render(
            lang=lang,
            dir=language_dir(lang),
            head=head,
            css_href=ctx.rel(CSS_PATH),
            js_href=ctx.rel(JS_PATH),
            home_href=ctx.rel(home),
            site=ctx.site_view(),
            header=ctx.header_view(first_section),
            nav=ctx.nav(),
            languages=languages,
            sections_html=sections_html,
            doc=doc,
            ctx=ctx,
            preview=preview is not None,
            inline_css=compose_css(doc, preview.font_base) if preview else None,
            inline_js=(STATIC / "site.js").read_text() if preview else None,
            preview_js=(STATIC / ("live.js" if preview.interactive else "preview.js")).read_text()
            if preview
            else None,
        )
    )


SOCIAL_CARD_PATH = "social-card.png"


def _social_image_url(doc: SiteDocument, ctx: RenderContext, asset_id: str | None) -> str | None:
    path = ctx.asset_path(asset_id) if asset_id else None
    if path is None and ctx.social_card:
        path = SOCIAL_CARD_PATH  # no picture chosen: fall back to the generated card
    return f"{doc.site.base_url}/{path}" if path and doc.site.base_url else None


def render_page(
    doc: SiteDocument,
    page: Page,
    lang: str,
    assets: dict[str, AssetFile],
    issues: list[Issue],
    *,
    out_path: str | None = None,
    absolute: bool = False,
    preview: PreviewOptions | None = None,
    posts: list[Post] | None = None,
    social_card: bool = False,
) -> str:
    """Render one page in one language. `out_path`/`absolute` are for synthetic pages (404)."""
    plan = paths.plan_pages(doc)
    out_path = out_path or plan[(page.id, lang)]
    is_real_page = (page.id, lang) in plan
    ctx = RenderContext(
        doc,
        lang,
        out_path,
        assets,
        issues,
        absolute=absolute,
        page_id=page.id if is_real_page else None,
        preview=preview,
        posts=posts,
        social_card=social_card,
    )
    wrapper = get_env().get_template("_section.html.j2")
    sections_html = [
        wrapper.render(
            s=section,
            p=localized_props(section, lang, doc.site.default_language),
            ctx=ctx,
            preview=ctx.editing,
            empty_hint=_empty_hint(section, lang, doc) if ctx.editing else None,
        )
        for section in page.sections
    ]
    site = ctx.site_view()
    head = {
        "title": seo.page_title(doc, page, lang, site["name"], site["tagline"])
        if doc.pages
        else page.title,
        "description": seo.page_description(doc, page, lang, site["description"]),
        "canonical": seo.public_url(doc, out_path) if is_real_page else None,
        "image": _social_image_url(doc, ctx, page.seo.social_image or doc.site.seo.social_image),
        "noindex": page.seo.noindex or not is_real_page,
        "alternates": seo.alternates(doc, page, plan) if is_real_page else [],
        "og_type": "website",
        "favicon": favicon_href(doc, site["name"], ctx),
        # the home page carries the business record; it is skipped in previews and on the 404
        "jsonld": jsonld.business(site, doc.site.base_url, doc.site.business.social)
        if is_real_page and page is doc.pages[0] and preview is None
        else None,
    }
    return _render_layout(
        doc,
        lang,
        ctx,
        sections_html,
        head,
        preview,
        ctx.language_links(),
        first_section=page.sections[0] if page.sections else None,
    )


def favicon_href(doc: SiteDocument, site_name: str, ctx: "RenderContext | None" = None) -> str:
    """The favicon: the uploaded logo (its smallest copy) when there is one, otherwise an inline SVG
    (site initial on the brand color) that needs no file and no request."""
    if ctx and doc.site.logo and not ctx.preview:
        asset = ctx.assets.get(doc.site.logo.asset)
        if asset:
            if asset.variants:
                width = min(w for w, _ in asset.variants)
                return ctx.rel(variant_output_path(doc.site.logo.asset, asset, width))
            return ctx.rel(asset_output_path(doc.site.logo.asset, asset))
    primary = doc.theme.palette["primary"]
    letter = (site_name.strip()[:1] or "S").upper()
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{primary}"/>'
        f'<text x="32" y="44" font-family="Georgia,serif" font-size="36" font-weight="700" '
        f'text-anchor="middle" fill="{readable_on(primary)}">{escape(letter)}</text></svg>'
    )
    return "data:image/svg+xml," + quote(svg)


def blog_index_path(doc: SiteDocument, lang: str) -> str:
    """Where "Back to blog" goes: the first page showing a blog list, else the home page."""
    plan = paths.plan_pages(doc)
    for page in doc.pages:
        if any(s.type == "blog_list" for s in page.sections):
            return plan[(page.id, lang)]
    return plan[(doc.pages[0].id, lang)]


def render_post(
    doc: SiteDocument,
    post: Post,
    assets: dict[str, AssetFile],
    issues: list[Issue],
    all_posts: list[Post],
    *,
    preview: PreviewOptions | None = None,
    social_card: bool = False,
) -> str:
    lang = post.lang
    out_path = paths.post_output_path(doc, post)
    ctx = RenderContext(
        doc,
        lang,
        out_path,
        assets,
        issues,
        preview=preview,
        posts=all_posts,
        social_card=social_card,
    )
    view = ctx.post_view(post)
    article = (
        get_env()
        .get_template("_post.html.j2")
        .render(
            post=view,
            body=ctx.md(post.body_md),
            ctx=ctx,
            back_href=ctx.rel(blog_index_path(doc, lang)),
        )
    )
    wrapper = (
        f'<section class="s sp-normal bg-default"><div class="container">{article}</div></section>'
    )
    site = ctx.site_view()
    translations = [p for p in all_posts if p.translation_group == post.translation_group]
    alternates = []
    languages = []
    if len(translations) > 1:
        for t in sorted(
            translations,
            key=lambda t: doc.site.languages.index(t.lang) if t.lang in doc.site.languages else 99,
        ):
            target = paths.post_output_path(doc, t)
            languages.append(
                {
                    "code": t.lang,
                    "label": strings.language_name(t.lang),
                    "href": ctx.rel(target),
                    "current": t.lang == lang,
                }
            )
            if doc.site.base_url:
                alternates.append((t.lang, seo.public_url(doc, target)))
    head = {
        "title": doc.site.seo.title_template.replace("{page}", post.title).replace(
            "{site}", site["name"]
        ),
        "description": post.excerpt or site["description"],
        "canonical": seo.public_url(doc, out_path),
        "image": _social_image_url(doc, ctx, post.cover or doc.site.seo.social_image),
        "noindex": False,
        "alternates": alternates,
        "og_type": "article",
        "favicon": favicon_href(doc, site["name"], ctx),
        "jsonld": jsonld.article(
            post.title,
            post.excerpt,
            seo.public_url(doc, out_path),
            post.published_at.date().isoformat(),
            site["name"],
            _social_image_url(doc, ctx, post.cover),
        )
        if preview is None
        else None,
    }
    return _render_layout(doc, lang, ctx, [wrapper], head, preview, languages)


def render_not_found(doc: SiteDocument, assets, issues: list[Issue]) -> str:
    """404.html: root-relative URLs because hosts serve it at whatever path was requested."""
    from sitegen.sections import create_section

    lang = doc.site.default_language
    hero = create_section("hero")
    hero.variant = "centered"
    hero.style.align = "center"
    hero.style.spacing = "spacious"
    hero.props.heading = strings.get(lang, "not_found_title")
    hero.props.subheading = strings.get(lang, "not_found_text")
    hero.props.buttons = []
    if doc.pages:
        hero.props.buttons = [
            Button(label=strings.get(lang, "back_home"), href=Link(page=doc.pages[0].id))
        ]
    page = Page.model_construct(
        id="pg_404",
        slug="404",
        title=hero.props.heading,
        seo=SEO(noindex=True),
        sections=[hero],
        i18n={},
    )
    return render_page(doc, page, lang, assets, issues, out_path="404.html", absolute=True)
