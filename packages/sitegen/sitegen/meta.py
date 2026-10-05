"""Static facts the editor needs to build its UI, derived from the models."""

from sitegen.icons import ICONS
from sitegen.models import SectionStyle
from sitegen.schema import RTL_LANGUAGES, Theme
from sitegen.sections import REGISTRY
from sitegen.starters import list_starters
from sitegen.strings import LANGUAGE_NAMES
from sitegen.theme import FONT_STACKS, RADII


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
        "fonts": list(FONT_STACKS),
        "radii": list(RADII),
        "languages": LANGUAGE_NAMES,
        "rtl_languages": sorted(RTL_LANGUAGES),
        "starters": list_starters(),
    }
