"""Titles, descriptions, canonical/alternate URLs, sitemap.xml and robots.txt."""

from xml.sax.saxutils import escape

from sitegen import paths
from sitegen.schema import Page, SiteDocument


def public_path(out_path: str) -> str:
    """Pretty public URL path for an output file: about/index.html -> /about/"""
    path = out_path.removesuffix("index.html")
    return "/" + path


def public_url(doc: SiteDocument, out_path: str) -> str | None:
    base = doc.site.base_url
    return f"{base}{public_path(out_path)}" if base else None


def page_title(doc: SiteDocument, page: Page, lang: str, site_name: str, tagline: str) -> str:
    tr = page.i18n.get(lang)
    explicit = (tr.seo_title if tr and tr.seo_title else None) or (
        page.seo.title if lang == doc.site.default_language else None
    )
    if explicit:
        return explicit
    page_name = tr.title if tr and tr.title else page.title
    if page is doc.pages[0]:  # home page: "Site - tagline"
        return f"{site_name} – {tagline}" if tagline else site_name
    return doc.site.seo.title_template.replace("{page}", page_name).replace("{site}", site_name)


def page_description(doc: SiteDocument, page: Page, lang: str, site_description: str) -> str:
    tr = page.i18n.get(lang)
    if tr and tr.seo_description:
        return tr.seo_description
    if lang == doc.site.default_language and page.seo.description:
        return page.seo.description
    return site_description


def alternates(doc: SiteDocument, page: Page, plan: dict) -> list[tuple[str, str]]:
    """[(hreflang, absolute url)] for every language of a page, plus x-default."""
    if len(doc.site.languages) < 2 or not doc.site.base_url:
        return []
    alts = [(lang, public_url(doc, plan[(page.id, lang)])) for lang in doc.site.languages]
    alts.append(("x-default", public_url(doc, plan[(page.id, doc.site.default_language)])))
    return alts


def sitemap_xml(doc: SiteDocument) -> str | None:
    if not doc.site.base_url:
        return None
    plan = paths.plan_pages(doc)
    rows = []
    for page in doc.pages:
        if page.seo.noindex:
            continue
        for lang in doc.site.languages:
            links = "".join(
                f'<xhtml:link rel="alternate" hreflang="{h}" href="{escape(u)}"/>'
                for h, u in alternates(doc, page, plan)
            )
            rows.append(
                f"<url><loc>{escape(public_url(doc, plan[(page.id, lang)]))}</loc>{links}</url>"
            )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n"
    )


def robots_txt(doc: SiteDocument) -> str:
    lines = ["User-agent: *", "Allow: /"]
    if doc.site.base_url:
        lines.append(f"Sitemap: {doc.site.base_url}/sitemap.xml")
    return "\n".join(lines) + "\n"
