from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content
from sitegen.sections.base import SectionDef


class YoutubeProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    url: str = content("text", "", hint="Paste a YouTube link, e.g. https://youtu.be/…")
    caption: str = content("text", "")


class YoutubeSection(BaseSection):
    type: Literal["youtube"] = "youtube"
    variant: Literal["wide", "narrow"] = "wide"
    props: YoutubeProps = Field(default_factory=YoutubeProps)


DEF = SectionDef(
    "youtube",
    "YouTube video",
    YoutubeSection,
    YoutubeProps,
    defaults={"heading": "Watch our story"},
    description="Embed a video by pasting its YouTube link. Loads only when clicked.",
)
