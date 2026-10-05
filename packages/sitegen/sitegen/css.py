"""Assembles the single stylesheet for a site: theme tokens + base + CSS of the sections used."""

from pathlib import Path

from sitegen.fonts import font_face_css
from sitegen.schema import SiteDocument
from sitegen.sections import REGISTRY
from sitegen.theme import theme_css

STATIC = Path(__file__).parent / "static"


def compose_css(doc: SiteDocument, font_base: str = "../fonts/") -> str:
    used = {s.type for page in doc.pages for s in page.sections}
    parts = [font_face_css(doc, font_base), theme_css(doc.theme), (STATIC / "base.css").read_text()]
    parts += [REGISTRY[t].css() for t in sorted(used)]  # only sections actually used
    return "\n".join(p for p in parts if p)
