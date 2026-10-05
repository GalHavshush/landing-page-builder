"""Section registry. To add a section type: create sections/<type>/ and list it here."""

from typing import Annotated, Union

from pydantic import Field

from sitegen.sections.base import SectionDef
from sitegen.sections.hero.model import DEF as HERO
from sitegen.sections.text.model import DEF as TEXT

REGISTRY: dict[str, SectionDef] = {d.type: d for d in (HERO, TEXT)}

Section = Annotated[
    Union[tuple(d.section_model for d in REGISTRY.values())],  # noqa: UP007
    Field(discriminator="type"),
]
