from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Link, Strict, content, ui
from sitegen.sections.base import SectionDef


class LogoItem(Strict):
    image: ImageRef | None = ui("image", None)
    link: Link | None = ui("link", None)


class LogosProps(Strict):
    heading: str = content("text", "")
    items: list[LogoItem] = content("repeater", default_factory=list)


class LogosSection(BaseSection):
    type: Literal["logos"] = "logos"
    variant: Literal["row", "grid"] = "row"
    props: LogosProps = Field(default_factory=LogosProps)


DEF = SectionDef(
    "logos",
    "Logos",
    LogosSection,
    LogosProps,
    defaults={"heading": "Trusted by"},
    description="A row of client, partner or press logos, quiet until hovered.",
)
