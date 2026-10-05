from sitegen import build


def test_basic_page_matches_golden(basic_doc, golden):
    result = build(basic_doc)
    assert not result.issues
    golden("basic_index.html", result.files["index.html"].decode())


def test_markdown_is_sanitised(basic_doc):
    html = build(basic_doc).files["index.html"].decode()
    assert "<strong>love</strong>" in html
    assert "<script>" not in html
