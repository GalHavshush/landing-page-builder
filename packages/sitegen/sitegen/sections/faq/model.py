from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content
from sitegen.sections.base import SectionDef


class FaqItem(Strict):
    question: str = ""
    answer: str = ""  # Markdown


class FaqProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[FaqItem] = content("repeater", default_factory=list)


class FaqSection(BaseSection):
    type: Literal["faq"] = "faq"
    variant: Literal["accordion"] = "accordion"
    props: FaqProps = Field(default_factory=FaqProps)


DEF = SectionDef(
    "faq",
    "FAQ",
    FaqSection,
    FaqProps,
    defaults={
        "heading": "Frequently asked questions",
        "items": [
            {"question": "How do I get started?", "answer": "Just get in touch and we will help."},
            {"question": "What are your opening hours?", "answer": "See the footer for our hours."},
        ],
    },
    description="Questions and answers that expand when clicked.",
)
