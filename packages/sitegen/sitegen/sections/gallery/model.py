from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Strict, content, design, ui
from sitegen.sections.base import SectionDef


class GalleryItem(Strict):
    image: ImageRef | None = ui("image", None)
    caption: str = ui("text", "")


class GalleryProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[GalleryItem] = content("repeater", default_factory=list)
    columns: Literal[2, 3, 4] = design("segmented", 3)


class GallerySection(BaseSection):
    type: Literal["gallery"] = "gallery"
    variant: Literal["grid", "masonry", "mosaic"] = "grid"
    props: GalleryProps = Field(default_factory=GalleryProps)


DEF = SectionDef(
    "gallery",
    "Gallery",
    GallerySection,
    GalleryProps,
    defaults={"heading": "Gallery"},
    description="A grid of photos with optional captions.",
)
