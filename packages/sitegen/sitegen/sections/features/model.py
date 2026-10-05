from typing import Literal

from pydantic import Field
from sitegen.icons import IconName
from sitegen.models import BaseSection, Strict, content, design, ui
from sitegen.sections.base import SectionDef


class Feature(Strict):
    icon: IconName | None = ui("icon", None)
    title: str = ui("text", "")
    text: str = ui("textarea", "")


class FeaturesProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Feature] = content("repeater", default_factory=list)
    columns: Literal[2, 3, 4] = design("segmented", 3)


class FeaturesSection(BaseSection):
    type: Literal["features"] = "features"
    variant: Literal["cards", "plain"] = "cards"
    props: FeaturesProps = Field(default_factory=FeaturesProps)


DEF = SectionDef(
    "features",
    "Features",
    FeaturesSection,
    FeaturesProps,
    defaults={
        "heading": "Why choose us",
        "subheading": "A few things we do really well.",
        "items": [
            {"icon": "star", "title": "Quality", "text": "Made with care, every time."},
            {"icon": "clock", "title": "Fast", "text": "Quick turnaround you can rely on."},
            {"icon": "heart", "title": "Friendly", "text": "We treat every customer like family."},
        ],
    },
    description="A grid of short points, each with an icon, title and text.",
)
