import os
from pathlib import Path

import pytest
from sitegen import SiteDocument

GOLDEN = Path(__file__).parent / "golden"


def basic_doc_data() -> dict:
    return {
        "site": {"name": "Rosa Bakery", "tagline": "Fresh bread daily"},
        "pages": [
            {
                "id": "pg_home",
                "slug": "",
                "title": "Home",
                "sections": [
                    {
                        "id": "sec_hero",
                        "type": "hero",
                        "variant": "centered",
                        "props": {
                            "heading": "Bread worth waking up for",
                            "subheading": "Baked every morning at 5am.",
                            "buttons": [
                                {"label": "Say hello", "href": {"url": "mailto:hi@example.com"}}
                            ],
                        },
                    },
                    {
                        "id": "sec_text",
                        "type": "text",
                        "props": {
                            "heading": "Our story",
                            "body": "We **love** bread.\n\n<script>x</script>",
                        },
                    },
                ],
            }
        ],
    }


@pytest.fixture
def basic_doc() -> SiteDocument:
    return SiteDocument.model_validate(basic_doc_data())


@pytest.fixture
def golden():
    """Compare text to tests/golden/<name>; run with UPDATE_GOLDEN=1 to rewrite."""

    def check(name: str, actual: str) -> None:
        path = GOLDEN / name
        if os.environ.get("UPDATE_GOLDEN"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(actual)
        assert path.read_text() == actual, f"{name} differs; rerun with UPDATE_GOLDEN=1 to accept"

    return check
