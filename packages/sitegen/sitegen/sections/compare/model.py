from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Strict, content
from sitegen.sections.base import SectionDef


class CompareProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    before: ImageRef | None = content("image", None)
    after: ImageRef | None = content("image", None)
    before_label: str = content("text", "")
    after_label: str = content("text", "")
    caption: str = content("text", "")


class CompareSection(BaseSection):
    type: Literal["compare"] = "compare"
    variant: Literal["wide", "narrow"] = "wide"
    props: CompareProps = Field(default_factory=CompareProps)


DEF = SectionDef(
    "compare",
    "Before / after",
    CompareSection,
    CompareProps,
    defaults={"heading": "The difference"},
    description=(
        "Two photos with a slider to reveal one over the other. "
        "Great for renovations, hair, repairs."
    ),
)
