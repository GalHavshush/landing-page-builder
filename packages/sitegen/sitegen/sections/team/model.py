from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, ImageRef, Strict, content, design, ui
from sitegen.sections.base import SectionDef


class Member(Strict):
    name: str = ui("text", "")
    role: str = ui("text", "")
    bio: str = ui("textarea", "")
    photo: ImageRef | None = ui("image", None)


class TeamProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    items: list[Member] = content("repeater", default_factory=list)
    columns: Literal[2, 3, 4] = design("segmented", 3)


class TeamSection(BaseSection):
    type: Literal["team"] = "team"
    variant: Literal["cards", "round"] = "cards"
    props: TeamProps = Field(default_factory=TeamProps)


DEF = SectionDef(
    "team",
    "Team",
    TeamSection,
    TeamProps,
    defaults={
        "heading": "Meet the team",
        "subheading": "The people behind the work.",
        "items": [
            {"name": "Alex Morgan", "role": "Founder", "bio": "Started the business in 2015."},
            {
                "name": "Sam Rivera",
                "role": "Head of operations",
                "bio": "Keeps everything running smoothly.",
            },
            {
                "name": "Priya Shah",
                "role": "Customer care",
                "bio": "Usually the first friendly voice you hear.",
            },
        ],
    },
    description="Photos, names and roles of the people behind the business.",
)
