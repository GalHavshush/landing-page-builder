from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Link, Strict, content, ui
from sitegen.sections.base import SectionDef


class Plan(Strict):
    name: str = ui("text", "")
    price: str = ui("text", "")
    period: str = ui("text", "")
    description: str = ui("textarea", "")
    features: str = ui("textarea", "", hint="One per line")
    highlighted: bool = ui("toggle", False)
    cta_label: str = ui("text", "")
    cta_link: Link | None = ui("link", None)


class PricingProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    plans: list[Plan] = content("repeater", default_factory=list)


class PricingSection(BaseSection):
    type: Literal["pricing"] = "pricing"
    variant: Literal["cards"] = "cards"
    props: PricingProps = Field(default_factory=PricingProps)


DEF = SectionDef(
    "pricing",
    "Pricing",
    PricingSection,
    PricingProps,
    defaults={
        "heading": "Simple pricing",
        "plans": [
            {
                "name": "Basic",
                "price": "$19",
                "period": "per month",
                "features": "One thing\nAnother thing",
            },
            {
                "name": "Pro",
                "price": "$49",
                "period": "per month",
                "features": "Everything in Basic\nPriority support\nExtra features",
                "highlighted": True,
            },
            {
                "name": "Team",
                "price": "$99",
                "period": "per month",
                "features": "Everything in Pro\nMore seats",
            },
        ],
    },
    description="Plans or packages side by side, with a highlighted favourite.",
)
