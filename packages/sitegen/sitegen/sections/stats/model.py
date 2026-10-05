from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content, ui
from sitegen.sections.base import SectionDef


class Stat(Strict):
    value: str = ui("text", "", hint="e.g. 12,000+ or 98%")
    label: str = ui("text", "")


class StatsProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Stat] = content("repeater", default_factory=list)


class StatsSection(BaseSection):
    type: Literal["stats"] = "stats"
    variant: Literal["row", "cards"] = "row"
    props: StatsProps = Field(default_factory=StatsProps)


DEF = SectionDef(
    "stats",
    "Numbers",
    StatsSection,
    StatsProps,
    defaults={
        "items": [
            {"value": "10+", "label": "Years in business"},
            {"value": "2,500", "label": "Happy customers"},
            {"value": "98%", "label": "Would recommend us"},
            {"value": "24h", "label": "Typical reply time"},
        ]
    },
    description="Big numbers that count up when scrolled into view: years, customers, ratings.",
)
