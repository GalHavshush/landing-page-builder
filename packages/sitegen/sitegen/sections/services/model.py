from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Link, Strict, content, design
from sitegen.sections.base import SectionDef


class Service(Strict):
    title: str = ""
    description: str = ""
    price: str = ""
    image: ImageRef | None = None
    link: Link | None = None


class ServicesProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Service] = content("repeater", default_factory=list)
    columns: Literal[2, 3] = design("segmented", 3)


class ServicesSection(BaseSection):
    type: Literal["services"] = "services"
    variant: Literal["cards", "list"] = "cards"
    props: ServicesProps = Field(default_factory=ServicesProps)


DEF = SectionDef(
    "services",
    "Services",
    ServicesSection,
    ServicesProps,
    defaults={
        "heading": "Our services",
        "items": [
            {"title": "Consultation", "description": "Tell us what you need.", "price": "$50"},
            {
                "title": "Standard package",
                "description": "Our most popular option.",
                "price": "$150",
            },
            {"title": "Premium package", "description": "Everything included.", "price": "$300"},
        ],
    },
)
