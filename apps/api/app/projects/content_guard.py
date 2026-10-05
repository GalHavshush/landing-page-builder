"""Server-side enforcement of the content-only role (ADR 005).

An `editor` (the client) may change *content*: text and list items inside sections, business
info, translations, SEO texts. They may not change structure or design: add/remove/reorder
sections or pages, layout variants, styles, design props, theme, languages, menu, URLs.

The check is a whitelist merge, not a blacklist: start from the stored document, copy over
only the fields an editor is allowed to change from the submitted document, and require the
result to equal the submission. Anything else the client sent (or invented) makes the two
differ, so new fields added to the schema later are locked by default.
"""

import copy

from sitegen.sections import REGISTRY


def _merge_content(old: dict, new: dict) -> dict:
    merged = copy.deepcopy(old)

    # --- site-wide content -----------------------------------------------------------
    for key in ("tagline", "business", "i18n"):
        if key in new["site"]:
            merged["site"][key] = copy.deepcopy(new["site"][key])
    merged["site"]["footer"]["text"] = new["site"]["footer"]["text"]
    merged["site"]["seo"]["default_description"] = new["site"]["seo"]["default_description"]

    # --- pages: only content inside the existing pages and sections -----------------------
    new_pages = {p["id"]: p for p in new["pages"]}
    for page in merged["pages"]:
        incoming = new_pages.get(page["id"])
        if incoming is None:
            continue  # page removed: merged keeps it, so the comparison fails
        for key in ("title", "description", "social_image"):  # not `noindex`
            page["seo"][key] = incoming["seo"][key]
        # translations: only the SEO texts; translated titles and URL names are structure
        blank = {"title": None, "slug": None, "seo_title": None, "seo_description": None}
        merged_i18n = {}
        for lang in set(page["i18n"]) | set(incoming["i18n"]):
            tr = {**blank, **(page["i18n"].get(lang) or {})}
            src = incoming["i18n"].get(lang) or blank
            tr["seo_title"], tr["seo_description"] = src["seo_title"], src["seo_description"]
            merged_i18n[lang] = tr
        page["i18n"] = merged_i18n
        incoming_sections = {s["id"]: s for s in incoming["sections"]}
        for section in page["sections"]:
            src = incoming_sections.get(section["id"])
            if src is None or src.get("type") != section["type"]:
                continue
            for name in REGISTRY[section["type"]].translatable:  # content-group props only
                if name in src["props"]:
                    section["props"][name] = copy.deepcopy(src["props"][name])
            section["i18n"] = copy.deepcopy(src["i18n"])
    return merged


def changed_paths(a, b, path: str = "") -> list[str]:
    """Human-readable list of where two JSON values differ (for the error message)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: list[str] = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}/{key}")
            else:
                out += changed_paths(a[key], b[key], f"{path}/{key}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b) or any(
            isinstance(x, dict) and isinstance(y, dict) and x.get("id") != y.get("id")
            for x, y in zip(a, b, strict=False)
        ):
            return [path]  # items added, removed or reordered
        out = []
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            out += changed_paths(x, y, f"{path}/{i}")
        return out
    return [] if a == b else [path]


def _normalise(doc: dict) -> dict:
    """Drop empty translation entries so "no translation" has one representation."""
    doc = copy.deepcopy(doc)
    doc["site"]["i18n"] = {
        k: v for k, v in doc["site"]["i18n"].items() if any(x is not None for x in v.values())
    }
    for page in doc["pages"]:
        page["i18n"] = {
            k: v for k, v in page["i18n"].items() if any(x is not None for x in v.values())
        }
        for section in page["sections"]:
            section["i18n"] = {k: v for k, v in section["i18n"].items() if v}
    return doc


def content_violations(old: dict, new: dict) -> list[str]:
    """Paths the editor changed that they are not allowed to. Empty list = save is fine."""
    allowed, submitted = _normalise(_merge_content(old, new)), _normalise(new)
    return [] if allowed == submitted else changed_paths(allowed, submitted)
