from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content, ui
from sitegen.sections.base import SectionDef


class Step(Strict):
    title: str = ui("text", "")
    text: str = ui("textarea", "")


class StepsProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Step] = content("repeater", default_factory=list)


class StepsSection(BaseSection):
    type: Literal["steps"] = "steps"
    variant: Literal["horizontal", "timeline"] = "horizontal"
    props: StepsProps = Field(default_factory=StepsProps)


DEF = SectionDef(
    "steps",
    "Process",
    StepsSection,
    StepsProps,
    defaults={
        "heading": "How it works",
        "items": [
            {"title": "Get in touch", "text": "Tell us what you need. We reply within a day."},
            {"title": "We plan it", "text": "A clear plan and a fixed price, agreed up front."},
            {"title": "We deliver", "text": "Done properly, on time, and with a smile."},
        ],
    },
    description="A numbered process or timeline: how to order, what happens next.",
)
