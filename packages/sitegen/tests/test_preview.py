import pytest
from sitegen import AssetFile, build
from sitegen.meta import editor_meta
from sitegen.models import ImageRef
from sitegen.preview import render_preview
from sitegen.starters import load_starter


def test_preview_marks_sections_and_inlines_assets():
    doc = load_starter("clean")
    html = render_preview(doc, "pg_home").html
    assert 'data-section-id="sec_home_hero"' in html
    assert 'data-section-type="features"' in html
    assert "<style>" in html and 'rel="stylesheet"' not in html
    assert "section-click" in html  # editor script present


def test_preview_does_not_leak_into_real_builds():
    html = build(load_starter("clean")).files["index.html"].decode()
    assert "data-section-id" not in html and "section-click" not in html


def test_preview_links_do_not_navigate():
    html = render_preview(load_starter("clean"), "pg_home").html
    assert 'href="services/index.html"' not in html


def test_preview_uses_given_asset_urls_even_without_files():
    doc = load_starter("clean")
    doc.pages[0].sections[0].props.image = ImageRef(asset="a1", alt="x")
    doc.pages[0].sections[0].variant = "split"
    html = render_preview(doc, "pg_home", asset_url=lambda i: f"https://cdn.test/{i}").html
    assert 'src="https://cdn.test/a1"' in html


def test_preview_page_and_language_must_exist():
    with pytest.raises(KeyError):
        render_preview(load_starter("clean"), "nope")
    with pytest.raises(KeyError):
        render_preview(load_starter("clean"), "pg_home", lang="fr")


def test_editor_meta_describes_every_section_with_field_hints():
    meta = editor_meta()
    types = {s["type"] for s in meta["sections"]}
    assert {"hero", "features", "faq"} <= types
    hero = next(s for s in meta["sections"] if s["type"] == "hero")
    heading = hero["props_schema"]["properties"]["heading"]
    assert heading["group"] == "content" and heading["control"] == "text"
    assert hero["template"]["props"]["heading"]
    assert "split" in hero["variants"]


def test_assetfile_still_exported():
    assert AssetFile("a.png", b"x").filename == "a.png"


def test_post_preview_uses_the_given_font_base():
    from datetime import datetime

    from sitegen.posts import Post
    from sitegen.preview import render_post_preview
    from sitegen.starters import load_starter

    post = Post(
        id="p",
        lang="en",
        translation_group="g",
        slug="s",
        title="T",
        published_at=datetime(2026, 1, 1),
    )
    html = render_post_preview(load_starter("clean"), post, font_base="/api/fonts/").html
    assert "url(/api/fonts/" in html and "url(/fonts/" not in html


def test_empty_sections_get_a_hint_in_the_preview_only():
    from sitegen import SiteDocument
    from sitegen.sections import create_section

    logos = create_section("logos")  # no logos yet
    compare = create_section("compare")
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [
                {
                    "id": "pg",
                    "title": "A",
                    "sections": [logos.model_dump(mode="json"), compare.model_dump(mode="json")],
                }
            ],
        }
    )
    preview = render_preview(doc, "pg", "en").html
    assert preview.count('<div class="pv-empty">') == 2
    assert "pv-empty" not in build(doc).files["index.html"].decode()


def test_gallery_items_without_pictures_still_count_as_empty():
    from sitegen.sections import create_section, empty_hint
    from sitegen.sections.gallery.model import GalleryItem

    gallery = create_section("gallery")
    assert empty_hint("gallery", gallery.props)
    gallery.props.items = [GalleryItem()]
    assert "picture" in empty_hint("gallery", gallery.props)
    gallery.props.items = [GalleryItem(image=ImageRef(asset="a1", alt="x"))]
    assert empty_hint("gallery", gallery.props) is None
