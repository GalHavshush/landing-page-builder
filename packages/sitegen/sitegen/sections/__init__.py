"""Section registry. To add a section type: create sections/<type>/ and list it here."""

from typing import Annotated, Union

from pydantic import Field

from sitegen.sections.base import SectionDef
from sitegen.sections.blog_list.model import DEF as BLOG_LIST
from sitegen.sections.compare.model import DEF as COMPARE
from sitegen.sections.contact.model import DEF as CONTACT
from sitegen.sections.cta.model import DEF as CTA
from sitegen.sections.faq.model import DEF as FAQ
from sitegen.sections.features.model import DEF as FEATURES
from sitegen.sections.gallery.model import DEF as GALLERY
from sitegen.sections.hero.model import DEF as HERO
from sitegen.sections.hours.model import DEF as HOURS
from sitegen.sections.logos.model import DEF as LOGOS
from sitegen.sections.map.model import DEF as MAP
from sitegen.sections.pricing.model import DEF as PRICING
from sitegen.sections.services.model import DEF as SERVICES
from sitegen.sections.stats.model import DEF as STATS
from sitegen.sections.steps.model import DEF as STEPS
from sitegen.sections.team.model import DEF as TEAM
from sitegen.sections.testimonials.model import DEF as TESTIMONIALS
from sitegen.sections.text.model import DEF as TEXT
from sitegen.sections.youtube.model import DEF as YOUTUBE

REGISTRY: dict[str, SectionDef] = {
    d.type: d
    for d in (
        HERO,
        TEXT,
        FEATURES,
        SERVICES,
        GALLERY,
        TESTIMONIALS,
        PRICING,
        FAQ,
        CONTACT,
        YOUTUBE,
        MAP,
        BLOG_LIST,
        TEAM,
        HOURS,
        STATS,
        LOGOS,
        STEPS,
        CTA,
        COMPARE,
    )
}

Section = Annotated[
    Union[tuple(d.section_model for d in REGISTRY.values())],  # noqa: UP007
    Field(discriminator="type"),
]


def create_section(section_type: str):
    return REGISTRY[section_type].create()
