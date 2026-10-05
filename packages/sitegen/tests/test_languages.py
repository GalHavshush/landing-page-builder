import pytest
from pydantic import ValidationError
from sitegen import SiteDocument, build
from sitegen.starters import load_starter


def multilingual() -> SiteDocument:
    data = load_starter("clean").model_dump(mode="json")
    data["site"].update(
        base_url="https://example.com",
        languages=["en", "he"],
        i18n={"he": {"name": "סטודיו צפון", "tagline": "עיצוב מושכל"}},
    )
    data["site"]["nav"][1]["labels"] = {"he": "שירותים"}
    data["pages"][1]["i18n"] = {"he": {"title": "שירותים", "slug": "sherutim"}}
    hero = data["pages"][0]["sections"][0]
    hero["i18n"] = {"he": {"heading": "אנחנו עוזרים לעסק שלך"}}
    return SiteDocument.model_validate(data)


def test_languages_get_their_own_output_tree():
    files = build(multilingual()).files
    assert {"index.html", "he/index.html", "services/index.html", "he/sherutim/index.html"} <= set(
        files
    )


def test_rtl_language_sets_dir_and_lang():
    files = build(multilingual()).files
    assert '<html lang="he" dir="rtl">' in files["he/index.html"].decode()
    assert '<html lang="en" dir="ltr">' in files["index.html"].decode()


def test_translated_content_and_fallback():
    html = build(multilingual()).files["he/index.html"].decode()
    assert "אנחנו עוזרים לעסק שלך" in html  # translated
    assert "Absolutely wonderful" in html  # untranslated section falls back to default language
    assert "סטודיו צפון" in html
    assert "שירותים" in html  # translated nav label


def test_internal_links_stay_in_the_same_language():
    html = build(multilingual()).files["he/index.html"].decode()
    assert 'href="sherutim/index.html"' in html  # the hero button to the services page


def test_language_switcher_links_between_equivalent_pages():
    files = build(multilingual()).files
    he_services = files["he/sherutim/index.html"].decode()
    assert 'href="../../services/index.html" hreflang="en"' in he_services
    assert 'href="../../services/index.html"' in he_services
    assert 'hreflang="he" lang="he" aria-current="true"' in he_services
    en_home = files["index.html"].decode()
    assert 'href="he/index.html" hreflang="he"' in en_home


def test_hreflang_alternates_and_sitemap():
    files = build(multilingual()).files
    home = files["index.html"].decode()
    assert 'hreflang="he" href="https://example.com/he/"' in home
    assert 'hreflang="x-default" href="https://example.com/"' in home
    sitemap = files["sitemap.xml"].decode()
    assert "https://example.com/he/sherutim/" in sitemap
    assert 'hreflang="en" href="https://example.com/services/"' in sitemap


def test_single_language_site_has_no_switcher():
    html = build(load_starter("clean")).files["index.html"].decode()
    assert 'class="langs"' not in html


def test_translating_design_fields_or_unknown_languages_fails():
    data = multilingual().model_dump(mode="json")
    data["pages"][0]["sections"][0]["i18n"]["fr"] = {"heading": "x"}
    with pytest.raises(ValidationError, match="unknown or default languages"):
        SiteDocument.model_validate(data)


def test_duplicate_translated_slugs_fail():
    data = multilingual().model_dump(mode="json")
    data["pages"][2]["i18n"] = {"he": {"slug": "sherutim"}}
    with pytest.raises(ValidationError, match="duplicate page slugs"):
        SiteDocument.model_validate(data)


def test_404_has_no_switcher_and_is_default_language():
    html = build(multilingual()).files["404.html"].decode()
    assert 'class="langs"' not in html
    assert "Page not found" in html
