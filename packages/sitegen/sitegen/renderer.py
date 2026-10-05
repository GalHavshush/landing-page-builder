"""Turns a SiteDocument + one page + one language into an HTML string."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from sitegen import paths, seo, strings
from sitegen.icons import render_icon
from sitegen.markdown import render_markdown
from sitegen.models import Button, ImageRef, Link
from sitegen.schema import SEO, Page, SiteDocument, language_dir
from sitegen.sections import REGISTRY
from sitegen.sections.base import SECTIONS_DIR

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


@dataclass
class Issue:
    level: str  # "error" | "warning"
    message: str
    where: str = ""


@lru_cache(maxsize=1)
def get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader([str(TEMPLATES_DIR), str(SECTIONS_DIR)]),
        autoescape=True,  # every template is HTML
        undefined=StrictUndefined,
        lstrip_blocks=True,
    )


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
    ):
        self.doc = doc
        self.lang = lang
        self.out_path = out_path
        self.assets = assets
        self.issues = issues
        self.plan = paths.plan_pages(doc)
        self.page_id = page_id
        self.absolute = absolute  # root-relative URLs (needed for 404.html, served at any depth)

    def rel(self, target: str) -> str:
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
        path = self.asset_path(link.asset)
        if path is None:
            self.issues.append(Issue("warning", f"link to missing asset {link.asset!r}"))
            return "#"
        return self.rel(path)

    def image(self, ref: ImageRef | None) -> dict | None:
        if ref is None:
            return None
        path = self.asset_path(ref.asset)
        if path is None:
            self.issues.append(Issue("warning", f"missing image asset {ref.asset!r}"))
            return None
        asset = self.assets[ref.asset]
        return {
            "src": self.rel(path),
            "alt": ref.alt,
            "width": asset.width,
            "height": asset.height,
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
            "address": pick("address", site.business.address),
            "hours": pick("hours", site.business.hours),
            "footer_text": pick("footer_text", site.footer.text),
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

    def md(self, source: str) -> Markup:
        return Markup(render_markdown(source))  # noqa: S704 - sanitised by nh3


def asset_output_path(asset_id: str, asset: AssetFile) -> str:
    import hashlib
    import re

    digest = hashlib.sha256(asset.data).hexdigest()[:8]
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", asset.filename).strip("-") or "file"
    return f"assets/{digest}-{name}"


def render_page(
    doc: SiteDocument,
    page: Page,
    lang: str,
    assets: dict[str, AssetFile],
    issues: list[Issue],
    *,
    out_path: str | None = None,
    absolute: bool = False,
) -> str:
    """Render one page in one language. `out_path`/`absolute` are for synthetic pages (404)."""
    env = get_env()
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
    )
    wrapper = env.get_template("_section.html.j2")
    sections_html = [
        wrapper.render(
            s=section,
            p=localized_props(section, lang, doc.site.default_language),
            ctx=ctx,
        )
        for section in page.sections
    ]
    site = ctx.site_view()
    social_id = page.seo.social_image or doc.site.seo.social_image
    social_path = ctx.asset_path(social_id) if social_id else None
    head = {
        "title": seo.page_title(doc, page, lang, site["name"], site["tagline"])
        if doc.pages
        else page.title,
        "description": seo.page_description(doc, page, lang, site["description"]),
        "canonical": seo.public_url(doc, out_path) if is_real_page else None,
        "image": f"{doc.site.base_url}/{social_path}"
        if social_path and doc.site.base_url
        else None,
        "noindex": page.seo.noindex or not is_real_page,
        "alternates": seo.alternates(doc, page, plan) if is_real_page else [],
    }
    home = plan[(doc.pages[0].id, lang)] if doc.pages else out_path
    return env.get_template("layout.html.j2").render(
        lang=lang,
        dir=language_dir(lang),
        head=head,
        css_href=ctx.rel(CSS_PATH),
        js_href=ctx.rel(JS_PATH),
        home_href=ctx.rel(home),
        site=site,
        nav=ctx.nav(),
        languages=ctx.language_links(),
        sections_html=sections_html,
        doc=doc,
        ctx=ctx,
    )


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
