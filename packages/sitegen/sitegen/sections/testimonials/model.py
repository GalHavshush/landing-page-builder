from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Strict, content
from sitegen.sections.base import SectionDef


class Testimonial(Strict):
    quote: str = ""
    author: str = ""
    role: str = ""
    avatar: ImageRef | None = None


class TestimonialsProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Testimonial] = content("repeater", default_factory=list)


class TestimonialsSection(BaseSection):
    type: Literal["testimonials"] = "testimonials"
    variant: Literal["cards", "quote"] = "cards"
    props: TestimonialsProps = Field(default_factory=TestimonialsProps)


DEF = SectionDef(
    "testimonials",
    "Testimonials",
    TestimonialsSection,
    TestimonialsProps,
    defaults={
        "heading": "What customers say",
        "items": [
            {
                "quote": "Absolutely wonderful. Highly recommended!",
                "author": "Alex P.",
                "role": "Customer",
            },
            {"quote": "Great service and lovely people.", "author": "Sam R.", "role": "Customer"},
        ],
    },
)
