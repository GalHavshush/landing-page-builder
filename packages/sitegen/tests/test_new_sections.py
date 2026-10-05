import pytest
from pydantic import ValidationError
from sitegen import AssetFile, SiteDocument, build
from sitegen.models import ImageRef
from sitegen.sections import create_section
from sitegen.sections.contact.model import ContactProps
from sitegen.sections.gallery.model import GalleryItem
from sitegen.youtube import youtube_id


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ?t=42",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://youtube.com/shorts/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ&feature=share",
        "youtube.com/watch?v=dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
    ],
)
def test_youtube_id_formats(url):
    assert youtube_id(url) == "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "url", ["", "https://vimeo.com/123", "https://youtube.com/watch?v=short", "javascript:alert(1)"]
)
def test_youtube_id_rejects_non_youtube(url):
    assert youtube_id(url) is None


def render(section, **site) -> tuple[str, list]:
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T", **site},
            "pages": [{"id": "pg", "title": "A", "sections": [section.model_dump(mode="json")]}],
        }
    )
    result = build(doc)
    return result.files["index.html"].decode(), result.issues


def test_youtube_renders_privacy_friendly_facade_and_warns_on_bad_links():
    s = create_section("youtube")
    s.props.url = "https://youtu.be/dQw4w9WgXcQ"
    html, _ = render(s)
    assert 'data-yt="dQw4w9WgXcQ"' in html
    assert "youtube.com/watch?v=dQw4w9WgXcQ" in html  # no-JS fallback link
    assert "<iframe" not in html  # nothing loaded from YouTube until click
    s.props.url = "https://vimeo.com/1"
    html, issues = render(s)
    assert "data-yt" not in html
    assert any("YouTube" in i.message for i in issues)


def test_contact_form_posts_to_configured_endpoint_with_honeypot():
    s = create_section("contact")
    s.props.form_endpoint = "https://formspree.io/f/abc"
    html, _ = render(s, business={"email": "hi@x.com"})
    assert 'action="https://formspree.io/f/abc" method="post"' in html
    assert 'name="_gotcha"' in html
    assert 'name="email"' in html and 'name="message"' in html


def test_contact_form_falls_back_to_mailto_then_hides():
    s = create_section("contact")
    html, _ = render(s, business={"email": "hi@x.com"})
    assert 'action="mailto:hi@x.com"' in html and "text/plain" in html
    html, _ = render(s)  # no endpoint and no email: no form to submit anywhere
    assert "<form" not in html


def test_contact_shows_business_info_and_translated_labels():
    s = create_section("contact")
    html, _ = render(
        s,
        business={
            "phone": "+1 555",
            "address": "12 Main St",
            "hours": [{"label": "Mon", "open": "9", "close": "5"}],
        },
    )
    assert 'href="tel:+1 555"' in html and "12 Main St" in html and "Mon: 9&ndash;5" in html


def test_contact_endpoint_must_be_https():
    with pytest.raises(ValidationError):
        ContactProps(form_endpoint="http://insecure.example")
    with pytest.raises(ValidationError):
        ContactProps(form_endpoint="javascript:alert(1)")


def test_pricing_splits_feature_lines_and_marks_highlight():
    s = create_section("pricing")
    html, _ = render(s)
    assert html.count('class="plan ') + html.count('class="plan"') == 3
    assert "plan--hl" in html
    assert "<li>" in html and "Priority support" in html


def test_gallery_skips_items_without_an_image_and_renders_captions():
    s = create_section("gallery")
    s.props.items = [
        GalleryItem(image=None, caption="no image"),
        GalleryItem(image=ImageRef(asset="a1", alt="A loaf"), caption="Sourdough"),
    ]
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [{"id": "pg", "title": "A", "sections": [s.model_dump(mode="json")]}],
        }
    )
    html = (
        build(doc, {"a1": AssetFile("loaf.webp", b"x", width=10, height=10)})
        .files["index.html"]
        .decode()
    )
    assert "Sourdough" in html and "no image" not in html and 'alt="A loaf"' in html


def test_map_uses_business_address_when_query_is_empty():
    s = create_section("map")
    html, _ = render(s, business={"address": "12 Main St"})
    assert "q=12%20Main%20St" in html and 'loading="lazy"' in html
    html, _ = render(s)
    assert "<iframe" not in html


def hero_cover(**props):
    s = create_section("hero")
    s.variant = "cover"
    for key, value in props.items():
        setattr(s.props, key, value)
    return s


def test_cover_hero_is_full_bleed_with_text_over_the_image():
    s = hero_cover(image=ImageRef(asset="a1", alt="Loaves"), overlay="heavy", height="screen")
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [{"id": "pg", "title": "A", "sections": [s.model_dump(mode="json")]}],
        }
    )
    html = (
        build(doc, {"a1": AssetFile("loaf.webp", b"img", width=8, height=6)})
        .files["index.html"]
        .decode()
    )
    assert "hero-cover hc-screen ov-heavy" in html
    assert 'class="s s-hero s-hero--cover' in html and " bleed" in html
    section = html[html.index("<section") : html.index("</section>")]
    assert (
        section.count('class="container') == 1
    )  # only the text; the picture ignores the container
    assert (
        'aria-hidden="true"' in html and 'alt=""' in html
    )  # decorative: the text carries the meaning
    assert "<h1>Your headline here</h1>" in html


def test_cover_hero_video_is_a_deferred_youtube_background_with_a_pause_button():
    html, issues = render(hero_cover(video_url="https://youtu.be/dQw4w9WgXcQ"))
    assert 'data-yt-bg="dQw4w9WgXcQ"' in html
    assert "<iframe" not in html  # nothing is loaded from YouTube by the HTML itself
    assert 'class="cover-toggle"' in html and "Pause background video" in html
    assert not [i for i in issues if i.level == "warning" and "base_url" not in i.message]


def test_cover_hero_bad_video_link_warns_and_falls_back_to_the_picture():
    html, issues = render(hero_cover(video_url="https://vimeo.com/1"))
    assert "data-yt-bg" not in html and "cover-toggle" not in html
    assert any("YouTube" in i.message for i in issues)


def test_cover_hero_without_any_media_still_renders():
    html, _ = render(hero_cover())
    assert "hero-cover" in html and "<h1>" in html and "<img" not in html


def test_other_hero_layouts_are_unchanged():
    s = create_section("hero")
    html, _ = render(s)
    assert "hero-cover" not in html and 'class="container"' in html
