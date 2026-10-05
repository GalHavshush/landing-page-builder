"""Starter documents ("templates"): a theme plus pages of sections, stored as JSON files."""

import json
from pathlib import Path

from sitegen.schema import SiteDocument

STARTERS_DIR = Path(__file__).parent / "starters"


STARTER_INFO = {
    "clean": ("Clean business", "A neutral, modern look for services and small companies."),
    "warm": (
        "Local shop",
        "Warm colours and serif headings for bakeries, cafes and neighbourhood shops.",
    ),
    "minimal": ("Portfolio", "Quiet and spacious for freelancers, studios and personal sites."),
    "restaurant": (
        "Restaurant",
        "Dark, editorial and menu-led. Looks rich before you add a photo.",
    ),
    "salon": ("Salon & beauty", "Soft, airy and light-serif. Services, stylists and booking."),
    "trades": ("Trades & repairs", "Direct and trustworthy: call button, stats, how it works."),
    "clinic": ("Clinic & wellbeing", "Calm teal, doctors, opening hours and new-patient FAQ."),
    "photographer": ("Photographer", "Square, quiet and gallery-first. Lets the pictures lead."),
    "consultant": (
        "Consultant",
        "Confident navy and gold with logos, results and a call-booking CTA.",
    ),
    "gym": ("Gym & fitness", "Dark, bold and uppercase. Memberships, coaches and a free trial."),
    "landscaping": ("Garden & landscaping", "Fresh greens with before/after, services and quotes."),
}

# Where a real photo makes the biggest difference for each starter (shown to the owner).
PHOTO_HINTS = {
    "restaurant": [
        "Home hero: your dining room or best dish",
        "Menu: one photo per signature dish",
    ],
    "salon": ["Home hero: a finished cut or colour", "Stylists: a friendly portrait of each"],
    "trades": ["Home hero: you or your van at work", "Services: before and after of real jobs"],
    "clinic": [
        "Home hero: the reception or a doctor with a patient",
        "Doctors: a warm portrait of each",
    ],
    "photographer": [
        "Gallery: your 9 best images (Home and Portfolio)",
        "About: a portrait of you",
    ],
    "consultant": [
        "Logos: client logos you have permission to show",
        "Partners: professional headshots",
    ],
    "gym": ["Home hero: a class in action", "Coaches: an action shot of each"],
    "landscaping": ["Home hero: your best finished garden", "Before/after: one honest pair"],
    "clean": ["Home hero: a clear picture of your product or team"],
    "warm": ["Home hero: your shop front or best product", "Gallery: the bakery or kitchen"],
    "minimal": ["Home: a favourite piece of work"],
}


def starter_info() -> list[dict]:
    return [
        {
            "id": name,
            "label": STARTER_INFO.get(name, (name, ""))[0],
            "description": STARTER_INFO.get(name, (name, ""))[1],
            "theme": load_starter(name).theme.model_dump(mode="json"),
            "photo_hints": PHOTO_HINTS.get(name, []),
        }
        for name in list_starters()
    ]


def list_starters() -> list[str]:
    return sorted(p.stem for p in STARTERS_DIR.glob("*.json"))


def load_starter(name: str, site_name: str | None = None) -> SiteDocument:
    data = json.loads((STARTERS_DIR / f"{name}.json").read_text())
    if site_name:
        data["site"]["name"] = site_name
    return SiteDocument.model_validate(data)
