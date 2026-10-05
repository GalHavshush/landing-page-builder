from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Button, Strict, content
from sitegen.sections.base import SectionDef


class CtaProps(Strict):
    heading: str = content("text", "Ready to get started?")
    text: str = content("textarea", "")
    buttons: list[Button] = content("buttons", default_factory=list)


class CtaSection(BaseSection):
    type: Literal["cta"] = "cta"
    variant: Literal["banner", "split", "card"] = "banner"
    props: CtaProps = Field(default_factory=CtaProps)


DEF = SectionDef(
    "cta",
    "Call to action",
    CtaSection,
    CtaProps,
    defaults={
        "heading": "Ready to get started?",
        "text": "Tell us about your project and we will get back to you within a day.",
        "buttons": [{"label": "Get in touch", "href": {"url": "#contact"}}],
    },
    style={"background": "primary", "align": "center", "spacing": "normal"},
    description="A bold band that asks for one thing: call, book, buy or get in touch.",
)
