"""schema.org JSON-LD: helps search engines show hours, phone and address for local businesses."""

import json
import re

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_ABBR = {d[:3].lower(): i for i, d in enumerate(DAYS)}


def _day(token: str) -> int | None:
    return _ABBR.get(token.strip().lower()[:3]) if token.strip() else None


def parse_days(label: str) -> list[str]:
    """'Mon-Fri' -> Monday..Friday, 'Sat, Sun' -> Saturday, Sunday. Anything else -> []."""
    days: list[int] = []
    for part in re.split(r"[,&/]|\band\b", label):
        bits = re.split(r"\s*[-–—]\s*|\s+to\s+", part.strip())
        if len(bits) == 2 and _day(bits[0]) is not None and _day(bits[1]) is not None:
            a, b = _day(bits[0]), _day(bits[1])
            days += list(range(a, b + 1)) if a <= b else list(range(a, 7)) + list(range(0, b + 1))
        elif len(bits) == 1 and _day(bits[0]) is not None:
            days.append(_day(bits[0]))
        else:
            return []
    return [DAYS[i] for i in dict.fromkeys(days)]


def _time(value: str) -> bool:
    return bool(re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", value.strip()))


def dumps(data: dict) -> str:
    """JSON safe to place inside a <script> element."""
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def business(
    site: dict, base_url: str, social: dict[str, str], logo_url: str | None = None
) -> str | None:
    """A LocalBusiness record, or None when there is nothing to say beyond the name."""
    has_contact = site["phone"] or site["email"] or site["address"] or site["hours"]
    if not has_contact:
        return None
    data: dict = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": site["name"]}
    if site["description"]:
        data["description"] = site["description"]
    if base_url:
        data["url"] = base_url + "/"
    if logo_url:
        data["image"] = logo_url
    if site["phone"]:
        data["telephone"] = site["phone"]
    if site["email"]:
        data["email"] = site["email"]
    if site["address"]:
        data["address"] = {"@type": "PostalAddress", "streetAddress": site["address"]}
    specs = []
    for h in site["hours"]:
        days = parse_days(h.label)
        if days and not h.closed and _time(h.open) and _time(h.close):
            specs.append(
                {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": days,
                    "opens": h.open.strip().zfill(5),
                    "closes": h.close.strip().zfill(5),
                }
            )
    if specs:
        data["openingHoursSpecification"] = specs
    links = [u for u in social.values() if u.startswith("https://")]
    if links:
        data["sameAs"] = links
    return dumps(data)


def article(
    title: str,
    description: str,
    url: str | None,
    published: str | None,
    site_name: str,
    image_url: str | None,
) -> str:
    data: dict = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title[:110],
        "publisher": {"@type": "Organization", "name": site_name},
    }
    if description:
        data["description"] = description
    if url:
        data["mainEntityOfPage"] = url
    if published:
        data["datePublished"] = published
    if image_url:
        data["image"] = image_url
    return dumps(data)
