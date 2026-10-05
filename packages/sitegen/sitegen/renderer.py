"""Turns a SiteDocument + one page + one language into an HTML string."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from sitegen import paths
from sitegen.markdown import render_markdown
from sitegen.models import ImageRef, Link
from sitegen.schema import Page, SiteDocument, language_dir
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
    return section.props.model_copy(
        update=REGISTRY[section.type]
        .props_model.model_validate({**section.props.model_dump(), **override})
        .model_dump()
    )


class RenderContext:
    """Per-page helpers exposed to templates as `ctx`."""

    def __init__(self, doc: SiteDocument, lang: str, out_path: str, assets, issues: list[Issue]):
        self.doc = doc
        self.lang = lang
        self.out_path = out_path
        self.assets = assets
        self.issues = issues
        self.plan = paths.plan_pages(doc)

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
            return paths.relative(self.out_path, target)
        path = self.asset_path(link.asset)
        if path is None:
            self.issues.append(Issue("warning", f"link to missing asset {link.asset!r}"))
            return "#"
        return paths.relative(self.out_path, path)

    def image(self, ref: ImageRef | None) -> dict | None:
        if ref is None:
            return None
        path = self.asset_path(ref.asset)
        if path is None:
            self.issues.append(Issue("warning", f"missing image asset {ref.asset!r}"))
            return None
        asset = self.assets[ref.asset]
        return {
            "src": paths.relative(self.out_path, path),
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
                    "href": paths.relative(self.out_path, target),
                    "current": target == self.out_path,
                }
            )
        return items

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
) -> str:
    env = get_env()
    out_path = paths.plan_pages(doc)[(page.id, lang)]
    ctx = RenderContext(doc, lang, out_path, assets, issues)
    wrapper = env.get_template("_section.html.j2")
    sections_html = [
        wrapper.render(
            s=section,
            p=localized_props(section, lang, doc.site.default_language),
            ctx=ctx,
        )
        for section in page.sections
    ]
    tr = page.i18n.get(lang)
    site = ctx.site_view()
    home = paths.plan_pages(doc)[(doc.pages[0].id, lang)] if doc.pages else out_path
    return env.get_template("layout.html.j2").render(
        lang=lang,
        dir=language_dir(lang),
        title=(tr.title if tr and tr.title else page.title),
        description=site["description"],
        css_href=paths.relative(out_path, CSS_PATH),
        js_href=paths.relative(out_path, JS_PATH),
        home_href=paths.relative(out_path, home),
        site=site,
        nav=ctx.nav(),
        sections_html=sections_html,
        doc=doc,
        ctx=ctx,
    )
