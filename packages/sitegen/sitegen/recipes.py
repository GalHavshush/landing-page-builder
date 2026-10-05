"""Page recipes: ready-made page layouts the editor offers when adding a page.

Each recipe is a title plus sections built from the section defaults with sensible copy. Sections
get fresh ids in the editor, so the ids here are only placeholders.
"""

from sitegen.sections import create_section


def _section(type_: str, variant: str | None = None, background: str | None = None, **props):
    s = create_section(type_)
    if variant:
        s.variant = variant
    if background:
        s.style.background = background
    for key, value in props.items():
        setattr(s.props, key, value)
    return s.model_dump(mode="json")


def _recipes() -> dict[str, dict]:
    return {
        "blank": {
            "label": "Blank page",
            "description": "Start empty and add your own sections.",
            "title": "New page",
            "sections": [],
        },
        "about": {
            "label": "About",
            "description": "Your story, how you work and the people behind it.",
            "title": "About us",
            "sections": [
                _section(
                    "text",
                    "split",
                    heading="Our story",
                    body="Tell visitors how you started and what you care about.\n\n"
                    "Keep it personal: who you are, who you help and why you do it.",
                ),
                _section("stats", "row", background="alt", heading=""),
                _section("team", "round", heading="The people behind it"),
                _section("cta", "banner", background="primary"),
            ],
        },
        "services": {
            "label": "Services",
            "description": "What you offer, how it works, and common questions.",
            "title": "Services",
            "sections": [
                _section("services", "cards", heading="What we do"),
                _section("steps", "horizontal", background="alt"),
                _section("faq", "accordion"),
                _section("cta", "banner", background="primary"),
            ],
        },
        "contact": {
            "label": "Contact",
            "description": "Contact form, opening hours and a map.",
            "title": "Contact",
            "sections": [
                _section("contact", "split"),
                _section("hours", "card", background="alt", show_contact=False),
                _section("map", "embedded"),
            ],
        },
        "pricing": {
            "label": "Pricing",
            "description": "Plans side by side with questions underneath.",
            "title": "Pricing",
            "sections": [
                _section("pricing", "cards"),
                _section("faq", "split", background="alt"),
                _section("cta", "card"),
            ],
        },
        "faq": {
            "label": "FAQ",
            "description": "Answers to the questions people ask most.",
            "title": "FAQ",
            "sections": [
                _section("faq", "accordion"),
                _section("cta", "banner", background="primary"),
            ],
        },
        "team": {
            "label": "Team",
            "description": "Photos and short bios of the people you work with.",
            "title": "Team",
            "sections": [
                _section("team", "cards"),
                _section("cta", "banner", background="primary"),
            ],
        },
        "portfolio": {
            "label": "Portfolio",
            "description": "A gallery of your work with a testimonial.",
            "title": "Portfolio",
            "sections": [
                _section("gallery", "masonry", heading="Selected work"),
                _section("testimonials", "quote", background="alt"),
            ],
        },
    }


def list_recipes() -> dict[str, dict]:
    return _recipes()
