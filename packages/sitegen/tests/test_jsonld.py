import json
import re
from datetime import datetime

import pytest
from sitegen import SiteDocument, build
from sitegen.jsonld import dumps, parse_days
from sitegen.posts import Post
from sitegen.starters import load_starter


@pytest.mark.parametrize(
    ("label", "days"),
    [
        ("Mon-Fri", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
        ("Sat", ["Saturday"]),
        ("Sat-Sun", ["Saturday", "Sunday"]),
        ("Mon, Wed", ["Monday", "Wednesday"]),
        ("Fri-Mon", ["Friday", "Saturday", "Sunday", "Monday"]),
        ("Weekends", []),
        ("Mon-Banana", []),
    ],
)
def test_parse_days(label, days):
    assert parse_days(label) == days


def test_dumps_cannot_close_the_script_tag():
    out = dumps({"name": "</script><script>alert(1)</script>"})
    assert "</script" not in out and "<" not in out


def ld(html: str) -> dict:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert m, "no JSON-LD"
    return json.loads(m.group(1))


def test_home_page_has_local_business_with_opening_hours():
    doc = load_starter("clean")
    doc.site.base_url = "https://example.com"
    html = build(doc).files["index.html"].decode()
    data = ld(html)
    assert data["@type"] == "LocalBusiness" and data["name"] == doc.site.name
    assert data["telephone"] == doc.site.business.phone
    spec = data["openingHoursSpecification"][0]
    assert spec["dayOfWeek"][0] == "Monday" and spec["opens"] == "09:00"
    # other pages do not repeat the business record
    assert "ld+json" not in build(doc).files["services/index.html"].decode()


def test_no_contact_info_means_no_business_record():
    doc = SiteDocument.model_validate(
        {"site": {"name": "T"}, "pages": [{"id": "p", "title": "A", "sections": []}]}
    )
    assert "ld+json" not in build(doc).files["index.html"].decode()


def test_blog_post_has_article_record():
    doc = load_starter("warm")
    doc.site.base_url = "https://example.com"
    post = Post(
        id="p1",
        lang="en",
        translation_group="g",
        slug="hello",
        title="Hello",
        excerpt="Hi there",
        body_md="Body",
        published_at=datetime(2026, 1, 5),
    )
    files = build(doc, posts=[post]).files
    path = next(p for p in files if p.endswith("hello/index.html"))
    data = ld(files[path].decode())
    assert data["@type"] == "BlogPosting" and data["datePublished"] == "2026-01-05"


def test_generated_social_card_is_used_only_when_no_image_chosen():
    doc = load_starter("clean")
    doc.site.base_url = "https://example.com"
    files = build(doc, social_card=b"PNGDATA").files
    assert files["social-card.png"] == b"PNGDATA"
    assert 'og:image" content="https://example.com/social-card.png"' in files["index.html"].decode()
    assert "social-card" not in build(doc).files["index.html"].decode()
