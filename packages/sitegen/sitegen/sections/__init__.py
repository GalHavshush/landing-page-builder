"""Section registry. To add a section type: create sections/<type>/ and list it here."""

from typing import Annotated, Union

from pydantic import Field

from sitegen.sections.base import SectionDef
from sitegen.sections.faq.model import DEF as FAQ
from sitegen.sections.features.model import DEF as FEATURES
from sitegen.sections.hero.model import DEF as HERO
from sitegen.sections.services.model import DEF as SERVICES
from sitegen.sections.testimonials.model import DEF as TESTIMONIALS
from sitegen.sections.text.model import DEF as TEXT

REGISTRY: dict[str, SectionDef] = {
    d.type: d for d in (HERO, TEXT, FEATURES, SERVICES, TESTIMONIALS, FAQ)
}

Section = Annotated[
    Union[tuple(d.section_model for d in REGISTRY.values())],  # noqa: UP007
    Field(discriminator="type"),
]


def create_section(section_type: str):
    return REGISTRY[section_type].create()
