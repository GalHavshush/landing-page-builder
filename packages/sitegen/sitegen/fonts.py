"""Web fonts: curated, open-licence (SIL OFL) variable fonts, bundled with the generator.

Why bundled: exported sites must work offline and anywhere (no Google Fonts request, no tracking,
no lock-in). Only the fonts a site actually uses, and only the scripts its languages need, are
copied into the export.  Files live in static/fonts/<key>/<subset>.woff2 (see manifest.json).
"""

import json
from functools import lru_cache
from pathlib import Path

from sitegen.schema import SiteDocument

FONTS_DIR = Path(__file__).parent / "static" / "fonts"

# Scripts a language needs beyond Latin. Latin + Latin Extended are always included.
LANG_SUBSETS = {
    "he": {"hebrew"},
    "yi": {"hebrew"},
    "ar": {"arabic"},
    "fa": {"arabic"},
    "ur": {"arabic"},
    "ru": {"cyrillic", "cyrillic-ext"},
    "uk": {"cyrillic", "cyrillic-ext"},
    "bg": {"cyrillic", "cyrillic-ext"},
    "sr": {"cyrillic", "cyrillic-ext"},
    "mk": {"cyrillic", "cyrillic-ext"},
    "be": {"cyrillic", "cyrillic-ext"},
}
SCRIPT_LABEL = {"hebrew": "Hebrew", "arabic": "Arabic", "cyrillic": "Cyrillic"}


@lru_cache(maxsize=1)
def manifest() -> dict:
    return json.loads((FONTS_DIR / "manifest.json").read_text())


def webfont_keys() -> list[str]:
    return list(manifest())


def is_webfont(key: str) -> bool:
    return key in manifest()


def font_stack(key: str, system_stacks: dict[str, str]) -> str:
    """CSS font-family value: the web font first, a system stack behind it while it loads or if a
    glyph is missing."""
    if key in system_stacks:
        return system_stacks[key]
    entry = manifest()[key]
    return f'"{entry["family"]}", {system_stacks["sans" if entry["kind"] == "sans" else "serif"]}'


def wanted_subsets(doc: SiteDocument) -> set[str]:
    wanted = {"latin", "latin-ext"}
    for lang in doc.site.languages:
        wanted |= LANG_SUBSETS.get(lang.split("-")[0], set())
    return wanted


def used_fonts(doc: SiteDocument) -> list[str]:
    seen: list[str] = []
    for key in doc.theme.fonts.values():
        if is_webfont(key) and key not in seen:
            seen.append(key)
    return seen


def _faces(doc: SiteDocument):
    wanted = wanted_subsets(doc)
    for key in used_fonts(doc):
        for face in manifest()[key]["faces"]:
            if face["subset"] in wanted or face["subset"].split("-")[0] in wanted:
                yield key, face


def font_files(doc: SiteDocument) -> dict[str, bytes]:
    """Output path -> bytes for every font file the site needs."""
    return {
        f"fonts/{face['file']}": (FONTS_DIR / face["file"]).read_bytes() for _, face in _faces(doc)
    }


def font_face_css(doc: SiteDocument, base: str) -> str:
    """@font-face rules. `base` is where the files are, relative to the stylesheet."""
    rules = []
    for key, face in _faces(doc):
        rules.append(
            f'@font-face{{font-family:"{manifest()[key]["family"]}";font-style:normal;'
            f"font-weight:{face['weight']};font-display:swap;"
            f'src:url({base}{face["file"]}) format("woff2");unicode-range:{face["range"]}}}'
        )
    return "\n".join(rules)


def missing_scripts(doc: SiteDocument) -> list[tuple[str, str]]:
    """[(font key, script)] where a chosen web font cannot draw a language the site uses."""
    out = []
    needed = wanted_subsets(doc) - {"latin", "latin-ext"}
    for key in used_fonts(doc):
        have = {f["subset"].split("-")[0] for f in manifest()[key]["faces"]}
        for script in sorted({s.split("-")[0] for s in needed} - have):
            out.append((key, script))
    return out
