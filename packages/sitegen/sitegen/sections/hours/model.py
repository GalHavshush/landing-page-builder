from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content, design
from sitegen.sections.base import SectionDef


class HoursProps(Strict):
    heading: str = content("text", "Opening hours")
    subheading: str = content("textarea", "")
    note: str = content("textarea", "", hint="e.g. Last orders 30 minutes before closing.")
    show_contact: bool = content("toggle", True)
    show_address: bool = design("toggle", True)


class HoursSection(BaseSection):
    type: Literal["hours"] = "hours"
    variant: Literal["card", "split"] = "card"
    props: HoursProps = Field(default_factory=HoursProps)


DEF = SectionDef(
    "hours",
    "Opening hours",
    HoursSection,
    HoursProps,
    description="Your opening hours, taken from Site settings so they are always up to date.",
)
