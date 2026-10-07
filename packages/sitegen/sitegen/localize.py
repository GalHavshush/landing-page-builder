"""Placeholder content in other languages.

The starters, section templates and page layouts are written in English. For a site in another
language the same documents are translated through a table (starters/<lang>.json, English text to
text); strings with no entry stay as they are. Only text fields are touched, never ids or settings.
"""

import json
from copy import deepcopy
from functools import cache
from pathlib import Path

from sitegen.fonts import LANG_SUBSETS, manifest

TABLES = Path(__file__).parent / "starters" / "i18n"
CURRENCY = {"he": "₪"}  # replaces "$" in prices
TEXT_KEYS = frozenset(
    "name tagline default_description heading subheading eyebrow title description text label role "
    "question answer quote author bio body features note submit_label cta_label address caption "
    "before_label after_label period price".split()
)


@cache
def _table(lang: str) -> dict[str, str]:
    path = TABLES / f"{lang}.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def has_table(lang: str) -> bool:
    return bool(_table(lang))


def _text(value: str, key: str, lang: str) -> str:
    table = _table(lang)
    if value in table:
        return table[value]
    if key == "price" and lang in CURRENCY:
        return value.replace("$", CURRENCY[lang])
    return value


def translate(obj, lang: str, key: str | None = None):
    """A deep copy of `obj` with its text fields translated (a no-op without a table)."""
    if not has_table(lang):
        return deepcopy(obj)
    if isinstance(obj, dict):
        return {k: translate(v, lang, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate(v, lang, key) for v in obj]
    if isinstance(obj, str) and key in TEXT_KEYS and obj.strip() and not obj.startswith("#"):
        return _text(obj, key, lang)
    return obj


def untranslated(obj, lang: str, key: str | None = None) -> list[str]:
    """Text fields that translate() would leave in English (used by the tests)."""
    if isinstance(obj, dict):
        return [s for k, v in obj.items() for s in untranslated(v, lang, k)]
    if isinstance(obj, list):
        return [s for v in obj for s in untranslated(v, lang, key)]
    if isinstance(obj, str) and key in TEXT_KEYS and obj.strip() and not obj.startswith("#"):
        return [] if _text(obj, key, lang) != obj or obj in _table(lang).values() else [obj]
    return []


def _scripts(key: str) -> set[str]:
    return {f["subset"].split("-")[0] for f in manifest()[key]["faces"]} - {"latin"}


def _fonts_for(fonts: dict[str, str], lang: str) -> dict[str, str]:
    """Swap fonts that lack the language's script for a bundled one that has it."""
    needed = LANG_SUBSETS.get(lang.split("-")[0], set()) & {"hebrew", "arabic"}
    out = dict(fonts)
    for role, key in fonts.items():
        if needed and key in manifest() and not needed <= _scripts(key):
            fits = [k for k in manifest() if needed <= _scripts(k)]
            same_kind = [k for k in fits if manifest()[k]["kind"] == manifest()[key]["kind"]]
            if fits:
                out[role] = (same_kind or fits)[0]
    return out


def localize_starter(data: dict, lang: str) -> dict:
    """A starter document (as loaded JSON) with its content and fonts in `lang`."""
    if not has_table(lang):
        return data
    out = dict(data)
    out["site"] = translate(data["site"], lang)
    out["pages"] = translate(data["pages"], lang)
    out["theme"] = {**data["theme"], "fonts": _fonts_for(data["theme"]["fonts"], lang)}
    return out
