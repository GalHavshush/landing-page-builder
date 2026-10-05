from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content
from sitegen.sections.base import SectionDef


class TextProps(Strict):
    heading: str = content("text", "")
    body: str = content("richtext", "")  # Markdown source


class TextSection(BaseSection):
    type: Literal["text"] = "text"
    variant: Literal["single", "columns"] = "single"
    props: TextProps = Field(default_factory=TextProps)


DEF = SectionDef(
    "text",
    "Text",
    TextSection,
    TextProps,
    defaults={"heading": "About us", "body": "Write something about your business here."},
)
