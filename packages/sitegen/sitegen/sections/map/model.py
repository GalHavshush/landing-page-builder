from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content, design
from sitegen.sections.base import SectionDef


class MapProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    query: str = content(
        "text", "", hint="An address or place name. Leave empty to use the business address."
    )
    height: Literal["short", "medium", "tall"] = design("segmented", "medium")


class MapSection(BaseSection):
    type: Literal["map"] = "map"
    variant: Literal["embedded"] = "embedded"
    props: MapProps = Field(default_factory=MapProps)


DEF = SectionDef(
    "map",
    "Map",
    MapSection,
    MapProps,
    defaults={"heading": "Find us"},
    description="A map showing your address.",
)
