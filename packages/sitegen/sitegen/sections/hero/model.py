from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Button, ImageRef, Strict, content, design
from sitegen.sections.base import SectionDef


class HeroProps(Strict):
    eyebrow: str = content("text", "")
    heading: str = content("text", "Your headline here")
    subheading: str = content("textarea", "")
    image: ImageRef | None = content("image", None)
    buttons: list[Button] = content("buttons", default_factory=list)
    image_position: Literal["start", "end"] = design("segmented", "end")


class HeroSection(BaseSection):
    type: Literal["hero"] = "hero"
    variant: Literal["centered", "split"] = "centered"
    props: HeroProps = Field(default_factory=HeroProps)


DEF = SectionDef(
    "hero",
    "Hero",
    HeroSection,
    HeroProps,
    defaults={
        "heading": "Your headline here",
        "subheading": "A short line that explains what you offer.",
        "buttons": [{"label": "Get in touch", "href": {"url": "#contact"}}],
    },
    description="A big headline with buttons and an optional image. Great at the top of a page.",
)
