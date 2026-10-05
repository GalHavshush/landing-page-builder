"""Stock photo search behind a small interface, so another provider can be added later.

Security: the browser only ever sends a *photo id*. The server asks the provider for that photo
and downloads it from a host on an allowlist over https, so a user can never make the server fetch
an arbitrary URL (SSRF). Downloads are size-capped and streamed.
"""

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

import httpx

PEXELS_API = "https://api.pexels.com/v1"
ALLOWED_IMAGE_HOSTS = {"images.pexels.com"}
MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
TIMEOUT = httpx.Timeout(10.0, connect=5.0)


class StockError(Exception):
    """The provider failed or returned something we refuse to use."""


@dataclass
class StockPhoto:
    id: str
    thumb_url: str
    full_url: str
    width: int
    height: int
    alt: str
    credit: str  # "Photo by Jane Doe on Pexels"
    page_url: str


class StockProvider(Protocol):
    name: str

    def search(self, query: str, page: int = 1) -> list[StockPhoto]: ...
    def get(self, photo_id: str) -> StockPhoto: ...
    def download(self, photo: StockPhoto) -> bytes: ...


def check_image_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_IMAGE_HOSTS or parsed.port:
        raise StockError("Refusing to download from an unexpected host")
    return url


class PexelsProvider:
    name = "pexels"

    def __init__(self, api_key: str, client: httpx.Client | None = None):
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=TIMEOUT, follow_redirects=False)

    def _json(self, path: str, **params) -> dict:
        try:
            r = self.client.get(
                f"{PEXELS_API}{path}", params=params, headers={"Authorization": self.api_key}
            )
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise StockError("The stock photo service is not available right now") from exc

    @staticmethod
    def _photo(raw: dict) -> StockPhoto:
        try:
            src = raw["src"]
            return StockPhoto(
                id=str(raw["id"]),
                thumb_url=check_image_url(src["medium"]),
                full_url=check_image_url(src.get("large2x") or src["large"]),
                width=int(raw["width"]),
                height=int(raw["height"]),
                alt=str(raw.get("alt") or "")[:300],
                credit=f"Photo by {raw.get('photographer', 'unknown')} on Pexels"[:300],
                page_url=str(raw.get("url", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise StockError("Unexpected response from the stock photo service") from exc

    def search(self, query: str, page: int = 1) -> list[StockPhoto]:
        data = self._json("/search", query=query, per_page=24, page=page, orientation="landscape")
        return [self._photo(p) for p in data.get("photos", [])]

    def get(self, photo_id: str) -> StockPhoto:
        if not photo_id.isdigit():
            raise StockError("Invalid photo id")
        return self._photo(self._json(f"/photos/{photo_id}"))

    def download(self, photo: StockPhoto) -> bytes:
        check_image_url(photo.full_url)
        chunks, total = [], 0
        try:
            with self.client.stream("GET", photo.full_url) as r:
                r.raise_for_status()
                for chunk in r.iter_bytes():
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise StockError("That photo is too large")
                    chunks.append(chunk)
        except httpx.HTTPError as exc:
            raise StockError("Could not download the photo") from exc
        return b"".join(chunks)
