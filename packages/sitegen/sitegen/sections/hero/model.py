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
    # "cover" layout only: an optional YouTube video plays muted behind the text
    # (the image stays visible as its poster)
    video_url: str = content(
        "text", "", hint="Cover layout: a YouTube link to play silently behind the text. Optional."
    )
    overlay: Literal["none", "light", "dark", "heavy"] = design(
        "segmented", "dark", hint="Cover layout: tint over the picture so the text stays readable."
    )
    height: Literal["medium", "tall", "screen"] = design("segmented", "tall")


class HeroSection(BaseSection):
    type: Literal["hero"] = "hero"
    variant: Literal["centered", "split", "cover"] = "centered"
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
    description=(
        "A big headline with buttons and an image. Choose centered, split, or a full-width "
        "cover with a photo or video behind the text."
    ),
)
