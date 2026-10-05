import pytest
from sitegen import AssetFile, SiteDocument, build
from sitegen.migrations import UnsupportedVersion, load_document, migrate
from sitegen.models import ImageRef
from sitegen.sections import create_section
from sitegen.starters import load_starter
from sitegen.validate import check


def messages(doc, assets=None):
    return [(i.level, i.message) for i in check(doc, assets)]


def test_starter_is_clean():
    assert not [i for i in check(load_starter("clean")) if i.level == "warning"]


def test_missing_alt_text_and_broken_link_are_warned():
    doc = load_starter("clean")
    hero = doc.pages[0].sections[0]
    hero.props.image = ImageRef(asset="a1", alt="")
    hero.props.buttons[0].href.page = "pg_gone"
    found = messages(doc, {"a1": AssetFile("x.png", b"x")})
    assert ("warning", "Image has no alt text") in found
    assert ("warning", "Link to unknown page 'pg_gone'") in found


def test_missing_asset_is_reported_by_build():
    doc = load_starter("clean")
    doc.pages[0].sections[0].props.image = ImageRef(asset="nope", alt="x")
    result = build(doc, {"other": AssetFile("o.png", b"o")})
    assert any("nope" in i.message for i in result.issues)


def test_low_contrast_palette_is_warned():
    data = load_starter("clean").model_dump(mode="json")
    data["theme"]["palette"]["text"] = "#BBBBBB"
    assert any("Low contrast" in m for _, m in messages(SiteDocument.model_validate(data)))


def test_missing_translations_are_info():
    data = load_starter("clean").model_dump(mode="json")
    data["site"]["languages"] = ["en", "he"]
    found = messages(SiteDocument.model_validate(data))
    assert any(level == "info" and "Not translated to he" in m for level, m in found)


def test_migrate_applies_steps_in_order():
    migrations = {1: lambda d: {**d, "a": 1}, 2: lambda d: {**d, "b": d["a"] + 1}}
    out = migrate({"schema_version": 1}, migrations, target=3)
    assert out == {"schema_version": 3, "a": 1, "b": 2}


def test_migrate_rejects_newer_and_unmigratable():
    with pytest.raises(UnsupportedVersion):
        migrate({"schema_version": 9}, {}, target=1)
    with pytest.raises(UnsupportedVersion):
        migrate({"schema_version": 1}, {}, target=2)


def test_load_document_roundtrip():
    doc = load_starter("clean")
    assert load_document(doc.model_dump(mode="json")) == doc


def test_new_section_has_no_warnings():
    doc = SiteDocument.model_validate(
        {
            "site": {"name": "T", "seo": {"default_description": "d"}},
            "pages": [{"title": "A", "sections": [create_section("hero").model_dump(mode="json")]}],
        }
    )
    assert not [i for i in check(doc) if i.level == "warning"]


def test_small_images_are_flagged_for_where_they_are_used():
    doc = load_starter("clean")
    hero = doc.pages[0].sections[0]
    hero.variant = "cover"
    hero.props.image = ImageRef(asset="a1", alt="x")
    small = {"a1": AssetFile("x.webp", b"x", width=900, height=600)}
    big = {"a1": AssetFile("x.webp", b"x", width=2200, height=1400)}
    assert any("900px wide" in m and "1600" in m for _, m in messages(doc, small))
    assert not any("blurry" in m for _, m in messages(doc, big))
    hero.variant = "split"  # smaller on screen, so 900px is plenty
    assert not any(
        "blurry" in m for _, m in messages(doc, {"a1": AssetFile("x.webp", b"x", width=1300)})
    )


def test_logo_alt_and_transparent_header_hints():
    doc = load_starter("clean")
    doc.site.logo = ImageRef(asset="a1", alt="")
    doc.site.header.transparent = True
    found = messages(doc)
    assert ("warning", "The logo has no alt text (use the business name)") in found
    assert any(level == "info" and "transparent header" in m for level, m in found)
    doc.pages[0].sections[0].variant = "cover"
    assert not any("transparent header" in m for _, m in messages(doc))
