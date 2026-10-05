import re

import pytest
from sitegen import SiteDocument, build
from sitegen.fonts import FONTS_DIR, manifest, missing_scripts, wanted_subsets
from sitegen.starters import load_starter
from sitegen.validate import check


def doc_with(heading="fraunces", body="dm-sans", languages=("en",)) -> SiteDocument:
    data = load_starter("clean").model_dump(mode="json")
    data["theme"]["fonts"] = {"heading": heading, "body": body}
    data["site"]["languages"] = list(languages)
    return SiteDocument.model_validate(data)


def font_paths(files) -> set[str]:
    return {p for p in files if p.startswith("fonts/")}


def test_every_manifest_file_exists_and_is_woff2():
    for key, entry in manifest().items():
        assert (FONTS_DIR / key / "OFL.txt").exists(), f"licence missing for {key}"
        assert any(f["subset"] == "latin" for f in entry["faces"])
        for face in entry["faces"]:
            assert (FONTS_DIR / face["file"]).read_bytes()[:4] == b"wOF2", face["file"]


def test_only_used_fonts_and_needed_scripts_are_exported():
    files = build(doc_with()).files
    paths = font_paths(files)
    assert paths == {
        "fonts/fraunces/latin.woff2",
        "fonts/fraunces/latin-ext.woff2",
        "fonts/dm-sans/latin.woff2",
        "fonts/dm-sans/latin-ext.woff2",
    }
    assert not any("manrope" in p or "heebo" in p for p in paths)


def test_system_fonts_ship_no_files():
    assert font_paths(build(doc_with("sans", "serif")).files) == set()


def test_css_has_self_hosted_font_face_with_relative_urls_and_a_fallback_stack():
    css = build(doc_with()).files["css/site.css"].decode()
    assert 'font-family:"Fraunces"' in css and "font-display:swap" in css
    assert "src:url(../fonts/fraunces/latin.woff2)" in css
    assert re.search(r'--font-heading: "Fraunces", "Fraunces Fallback", "Iowan Old Style"', css)
    assert "fonts.googleapis" not in css and "http" not in css.split("@font-face")[1].split("}")[0]


def test_hebrew_sites_get_the_hebrew_script_file():
    paths = font_paths(build(doc_with("heebo", "heebo", ("en", "he"))).files)
    assert "fonts/heebo/hebrew.woff2" in paths


def test_languages_map_to_scripts():
    assert wanted_subsets(doc_with(languages=("en", "he", "ru"))) >= {"hebrew", "cyrillic", "latin"}


def test_warns_when_a_font_cannot_draw_a_site_language():
    doc = doc_with("dm-sans", "dm-sans", ("en", "he"))
    assert ("dm-sans", "hebrew") in missing_scripts(doc)
    assert any("Hebrew" in i.message and "DM Sans" in i.message for i in check(doc))
    assert not [
        i for i in check(doc_with("heebo", "rubik", ("en", "he"))) if "letters" in i.message
    ]


def test_unknown_font_is_rejected():
    data = doc_with().model_dump(mode="json")
    data["theme"]["fonts"]["heading"] = "comic-sans"
    with pytest.raises(ValueError):
        SiteDocument.model_validate(data)


def test_preview_loads_fonts_from_the_given_base():
    from sitegen.preview import render_preview

    html = render_preview(
        doc_with(),
        "pg_home" if False else load_starter("clean").pages[0].id,
        font_base="/api/fonts/",
    ).html
    assert "url(/api/fonts/fraunces/latin.woff2)" in html


def test_web_fonts_get_a_metric_matched_fallback_face():
    from sitegen import build
    from sitegen.starters import load_starter

    doc = load_starter("clean")  # plus-jakarta + dm-sans
    css = build(doc).files["css/site.css"].decode()
    assert '@font-face{font-family:"DM Sans Fallback";src:local("Arial");size-adjust:' in css
    assert '"DM Sans", "DM Sans Fallback", system-ui' in css
    assert "Fraunces Fallback" not in css  # only fonts the site uses
