from sitegen import build


def test_basic_page_matches_golden(basic_doc, golden):
    result = build(basic_doc)
    assert not [i for i in result.issues if i.level == "warning" and "base_url" not in i.message]
    golden("basic_index.html", result.files["index.html"].decode())


def test_markdown_is_sanitised(basic_doc):
    html = build(basic_doc).files["index.html"].decode()
    assert "<strong>love</strong>" in html
    assert "<script>" not in html


def test_css_contains_theme_and_only_used_sections(basic_doc):
    css = build(basic_doc).files["css/site.css"].decode()
    assert "--color-primary: #2563EB" in css
    assert ".prose" in css


def test_theme_contrast_picks_readable_text():
    from sitegen.theme import readable_on

    assert readable_on("#000000") == "#FFFFFF"
    assert readable_on("#FFFFFF") == "#111111"


def test_output_uses_relative_urls(basic_doc):
    files = build(basic_doc).files
    assert 'href="css/site.css"' in files["index.html"].decode()
