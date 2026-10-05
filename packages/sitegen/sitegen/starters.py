"""Starter documents ("templates"): a theme plus pages of sections, stored as JSON files."""

import json
from pathlib import Path

from sitegen.schema import SiteDocument

STARTERS_DIR = Path(__file__).parent / "starters"


def list_starters() -> list[str]:
    return sorted(p.stem for p in STARTERS_DIR.glob("*.json"))


def load_starter(name: str, site_name: str | None = None) -> SiteDocument:
    data = json.loads((STARTERS_DIR / f"{name}.json").read_text())
    if site_name:
        data["site"]["name"] = site_name
    return SiteDocument.model_validate(data)
