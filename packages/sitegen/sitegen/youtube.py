"""Extract a YouTube video id from the URL shapes people paste."""

import re
from urllib.parse import parse_qs, urlparse

_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def youtube_id(url: str) -> str | None:
    url = (url or "").strip()
    if _ID.match(url):  # a bare id
        return url
    parsed = urlparse(url if "//" in url else f"https://{url}")
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    candidate = None
    if host == "youtu.be":
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif host in {"youtube.com", "youtube-nocookie.com"}:
        parts = [p for p in parsed.path.split("/") if p]
        if parts[:1] == ["watch"]:
            candidate = (parse_qs(parsed.query).get("v") or [None])[0]
        elif parts[:1] in (["embed"], ["shorts"], ["live"], ["v"]) and len(parts) > 1:
            candidate = parts[1]
    return candidate if candidate and _ID.match(candidate) else None
