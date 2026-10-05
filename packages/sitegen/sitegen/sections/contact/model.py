from typing import Literal

from pydantic import Field, field_validator
from sitegen.models import BaseSection, Strict, content, design
from sitegen.sections.base import SectionDef


class ContactProps(Strict):
    heading: str = content("text", "Get in touch")
    text: str = content("textarea", "")
    show_business_info: bool = content("toggle", True)
    show_form: bool = content("toggle", True)
    submit_label: str = content("text", "")  # empty -> the translated default "Send message"
    # Where the form posts to (Formspree, Web3Forms, your own endpoint...). Static sites have no
    # server of their own; with no endpoint the form opens the visitor's email app instead.
    form_endpoint: str = design(
        "text",
        "",
        hint="Paste the form URL from a service like Formspree. Leave empty to use the email app.",
    )

    @field_validator("form_endpoint")
    @classmethod
    def _https_only(cls, v: str) -> str:
        v = v.strip()
        if v and not v.lower().startswith("https://"):
            raise ValueError("form endpoint must start with https://")
        return v


class ContactSection(BaseSection):
    type: Literal["contact"] = "contact"
    variant: Literal["split", "stacked"] = "split"
    props: ContactProps = Field(default_factory=ContactProps)


DEF = SectionDef(
    "contact",
    "Contact",
    ContactSection,
    ContactProps,
    description="Contact details from your business info, plus a message form.",
)
