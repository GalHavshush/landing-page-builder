"""Where each page lives in the output, and how to link between files with relative URLs.

Relative URLs (not /absolute) keep the exported ZIP working from file:// or any subfolder.
Links end in index.html explicitly so they also work without a web server.
"""

import posixpath

from sitegen.schema import SiteDocument


def plan_pages(doc: SiteDocument) -> dict[tuple[str, str], str]:
    """(page_id, lang) -> output file path."""
    plan = {}
    for lang in doc.site.languages:
        prefix = "" if lang == doc.site.default_language else f"{lang}/"
        for page in doc.pages:
            slug = doc.page_slug(page, lang)
            plan[(page.id, lang)] = f"{prefix}{slug}/index.html" if slug else f"{prefix}index.html"
    return plan


def relative(from_file: str, to_file: str) -> str:
    start = posixpath.dirname(from_file) or "."
    return posixpath.relpath(to_file, start)
