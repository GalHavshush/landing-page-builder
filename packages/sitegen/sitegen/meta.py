"""Static facts the editor needs to build its UI, derived from the models."""

from sitegen.fonts import manifest
from sitegen.icons import ICONS
from sitegen.models import SectionStyle
from sitegen.recipes import list_recipes
from sitegen.schema import RTL_LANGUAGES, Theme
from sitegen.sections import REGISTRY
from sitegen.starters import list_starters, starter_info
from sitegen.strings import LANGUAGE_NAMES
from sitegen.theme import FONT_STACKS, RADII


def font_options() -> list[dict]:
    """Choices for the font pickers: system stacks first (no files), then bundled web fonts."""
    system = {
        "sans": "System sans",
        "serif": "System serif",
        "humanist": "Humanist",
        "rounded": "Rounded",
    }
    options = [
        {"key": k, "label": system[k], "kind": "system", "scripts": [], "file": None}
        for k in FONT_STACKS
    ]
    for key, entry in manifest().items():
        latin = next(f["file"] for f in entry["faces"] if f["subset"] == "latin")
        scripts = sorted({f["subset"].split("-")[0] for f in entry["faces"]} - {"latin"})
        options.append(
            {
                "key": key,
                "label": entry["family"],
                "kind": entry["kind"],
                "scripts": scripts,
                "file": latin,
            }
        )
    return options


def editor_meta() -> dict:
    sections = []
    for d in REGISTRY.values():
        template = d.create().model_dump(mode="json")
        sections.append(
            {
                "type": d.type,
                "label": d.label,
                "description": d.description,
                "variants": list(type(d.create()).model_fields["variant"].annotation.__args__),
                "template": template,  # a complete new section (the editor assigns a fresh id)
                # JSON Schema of the props; every property carries `group` and `control` hints
                "props_schema": d.props_model.model_json_schema(),
            }
        )
    return {
        "sections": sections,
        "section_style_schema": SectionStyle.model_json_schema(),
        "theme_schema": Theme.model_json_schema(),
        "icons": sorted(ICONS),
        "fonts": font_options(),
        "radii": list(RADII),
        "languages": LANGUAGE_NAMES,
        "rtl_languages": sorted(RTL_LANGUAGES),
        "starters": list_starters(),
        "starter_info": starter_info(),
        "page_recipes": list_recipes(),
    }
