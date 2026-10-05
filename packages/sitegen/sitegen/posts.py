"""Blog posts as the generator sees them (the SaaS stores them in a table; ADR 003/006).

Posts are not part of the site document: they are edited and published independently.
Each translation of a post is its own Post, linked by `translation_group`.
"""

import re
from datetime import datetime

from pydantic import field_validator

from sitegen.models import Strict

_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BLOG_DIR = "blog"


class Post(Strict):
    id: str
    lang: str
    translation_group: str
    slug: str
    title: str
    excerpt: str = ""
    body_md: str = ""
    cover: str | None = None  # asset id
    published_at: datetime

    @field_validator("slug")
    @classmethod
    def _slug(cls, v: str) -> str:
        if not _SLUG.match(v):
            raise ValueError("slug must be lowercase letters, digits and single hyphens")
        return v


def sort_newest_first(posts: list[Post]) -> list[Post]:
    return sorted(posts, key=lambda p: (p.published_at, p.id), reverse=True)


MONTHS = {
    "en": "January February March April May June July August September October November December",
    "he": "ינואר פברואר מרץ אפריל מאי יוני יולי אוגוסט ספטמבר אוקטובר נובמבר דצמבר",
    "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre "
    "diciembre",
    "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember",
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre",
    "ar": "يناير فبراير مارس أبريل مايو يونيو يوليو أغسطس سبتمبر أكتوبر نوفمبر ديسمبر",
}


def format_date(dt: datetime, lang: str) -> str:
    months = (MONTHS.get(lang) or MONTHS.get(lang.split("-")[0]) or MONTHS["en"]).split()
    return f"{dt.day} {months[dt.month - 1]} {dt.year}"
