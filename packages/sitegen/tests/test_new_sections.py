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


def one(section_type, variant, **props):
    s = create_section(section_type)
    s.variant = variant
    for key, value in props.items():
        setattr(s.props, key, value)
    html, _ = render(s)
    return html


def test_features_list_and_numbered_layouts():
    html = one("features", "list")
    assert 'class="feat-split"' in html and 'class="feat-rows"' in html
    numbered = one("features", "numbered")
    assert 'class="num"' in numbered and ">01<" in numbered and ">03<" in numbered
    assert "icon-wrap" not in numbered  # numerals replace icons


def test_services_alternating_keeps_the_same_items():
    html = one("services", "alternating")
    assert "s-services--alternating" in html and html.count("<article") == 3


def test_text_split_and_lead_layouts():
    assert "s-text--split" in one("text", "split") and 'class="text-wrap"' in one("text", "split")
    assert "s-text--lead" in one("text", "lead")


def test_faq_split_and_testimonial_columns():
    assert 'class="faq-split"' in one("faq", "split") and html_has_details(one("faq", "split"))
    assert "cols-3" in one("testimonials", "columns") and "s-testimonials--columns" in one(
        "testimonials", "columns"
    )


def html_has_details(html: str) -> bool:
    return html.count("<details>") >= 2


def test_gallery_mosaic_and_blog_featured_and_hero_banner():
    assert "s-gallery--mosaic" in one("gallery", "mosaic")
    assert "s-blog_list--featured" in one("blog_list", "featured")
    banner = one("hero", "banner")
    assert (
        'class="hero-banner"' in banner
        and 'class="hb-head"' in banner
        and "hero-cover" not in banner
    )


def test_images_get_srcset_placeholder_color_and_focus_point():
    from sitegen.models import Focus

    s = create_section("gallery")
    s.props.items = [
        GalleryItem(image=ImageRef(asset="a1", alt="Loaf", focus=Focus(x=20, y=80)), caption="")
    ]
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [{"id": "pg", "title": "A", "sections": [s.model_dump(mode="json")]}],
        }
    )
    asset = AssetFile(
        "loaf.webp",
        b"big",
        width=1600,
        height=1000,
        variants=[(480, b"s"), (960, b"m")],
        color="#b07a4a",
    )
    files = build(doc, {"a1": asset}).files
    html = files["index.html"].decode()
    assert " 480w," in html and " 960w," in html and " 1600w" in html and "sizes=" in html
    assert "background-color:#b07a4a" in html and "object-position:20% 80%" in html
    assert 'width="1600" height="1000"' in html and 'decoding="async"' in html
    variants = [p for p in files if p.startswith("assets/") and p.endswith("w.webp")]
    assert len(variants) == 2  # the smaller copies are shipped next to the main file


def test_images_without_variants_keep_a_plain_src():
    s = create_section("gallery")
    s.props.items = [GalleryItem(image=ImageRef(asset="a1", alt="Loaf"), caption="")]
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
    assert "srcset" not in html and "object-position" not in html


def test_hours_reads_business_info_and_warns_when_empty():
    s = create_section("hours")
    html, issues = render(s)
    assert any("opening hours" in i.message for i in issues)
    html, issues = render(
        s,
        business={
            "phone": "555-0100",
            "hours": [{"label": "Mon-Fri", "open": "09:00", "close": "17:00"}],
        },
    )
    assert "Mon-Fri" in html and "09:00" in html and "tel:555-0100" in html
    assert not any("opening hours" in i.message for i in issues)


def test_stats_markup_has_count_hook():
    s = create_section("stats")
    html, _ = render(s)
    assert 'class="stats' in html and "data-count" in html


def test_cta_defaults_to_primary_background():
    s = create_section("cta")
    assert s.style.background == "primary" and s.style.align == "center"


def test_compare_needs_both_images():
    s = create_section("compare")
    html, issues = render(s)
    assert any("before and an after" in i.message for i in issues)


@pytest.mark.parametrize("variant", ["round", "cards"])
def test_team_variants_render_initial_placeholder_without_photo(variant):
    s = create_section("team")
    s.variant = variant
    s.props.items[0].photo = None
    html, _ = render(s)
    assert s.props.items[0].name[0] in html


def test_fit_cols_avoids_empty_columns():
    from sitegen.renderer import fit_cols

    assert [fit_cols(3, n) for n in (1, 2, 3, 4, 5, 6)] == [1, 2, 3, 2, 3, 3]
    assert fit_cols(4, 4) == 4 and fit_cols(2, 1) == 1


def test_page_recipes_build_cleanly():
    from sitegen.recipes import list_recipes

    for key, recipe in list_recipes().items():
        if key == "blank":
            continue
        doc = SiteDocument.model_validate(
            {
                "site": {"name": "T", "base_url": "https://x.test"},
                "pages": [{"id": "pg", "title": recipe["title"], "sections": recipe["sections"]}],
            }
        )
        issues = [i for i in build(doc).issues if i.level == "warning"]
        assert not issues, (key, issues)


def test_gallery_images_link_to_full_size_for_the_lightbox():
    s = create_section("gallery")
    s.props.items = [GalleryItem(image=ImageRef(asset="a1", alt="One"), caption="First")]
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [{"id": "p", "title": "A", "sections": [s.model_dump(mode="json")]}],
        }
    )
    asset = AssetFile("a.png", b"x", "image/png", 800, 600)
    html = build(doc, {"a1": asset}).files["index.html"].decode()
    assert 'class="lb"' in html and "data-lb" in html and 'data-lb-close="Close"' in html


@pytest.mark.parametrize("motion", ["none", "subtle", "lively"])
def test_motion_setting_is_a_body_class(motion):
    from sitegen.starters import load_starter

    doc = load_starter("clean")
    doc.theme.motion = motion
    assert f"motion-{motion}" in build(doc).files["index.html"].decode()


@pytest.mark.parametrize("color", ["#F59E0B", "#FACC15", "#2563EB", "#FFFFFF", "#111111"])
@pytest.mark.parametrize(("bg", "surface"), [("#FFFFFF", "#F3F4F6"), ("#0F172A", "#1E293B")])
def test_legible_on_always_reaches_text_contrast(color, bg, surface):
    from sitegen.theme import contrast_ratio, legible_on

    out = legible_on(color, [bg, surface])
    assert contrast_ratio(out, bg) >= 4.5 and contrast_ratio(out, surface) >= 4.5
