import pytest
from sitegen import AssetFile, SiteDocument, build
from sitegen.starters import load_starter


def doc_with(**site) -> SiteDocument:
    data = load_starter("clean").model_dump(mode="json")
    data["site"].update(site)
    return SiteDocument.model_validate(data)


def html_of(doc, path="index.html", assets=None) -> str:
    return build(doc, assets).files[path].decode()


def test_default_header_is_classic_sticky_without_extras():
    html = html_of(doc_with())
    assert "hdr-classic" in html and "hdr-static" not in html
    assert 'class="announce"' not in html and "hdr-cta" not in html


@pytest.mark.parametrize("style", ["classic", "centered", "split"])
def test_every_header_style_renders_brand_nav_and_toggle(style):
    html = html_of(
        doc_with(header={"style": style, "sticky": True, "transparent": False, "cta": None})
    )
    assert f"hdr-{style}" in html
    assert 'class="brand"' in html and 'class="nav"' in html and "nav-toggle" in html


def test_header_cta_and_its_translation():
    cta = {"label": "Book now", "href": {"page": "pg_about"}, "style": "primary"}
    doc = doc_with(
        header={"style": "classic", "sticky": True, "transparent": False, "cta": cta},
        languages=["en", "he"],
        i18n={"he": {"cta_label": "הזמינו עכשיו"}},
    )
    en, he = html_of(doc), html_of(doc, "he/index.html")
    assert 'class="btn btn-primary hdr-cta" href="about/index.html">Book now' in en
    assert "הזמינו עכשיו" in he and "Book now" not in he


def test_announcement_bar_only_when_enabled_and_has_text():
    on = doc_with(
        announcement={
            "enabled": True,
            "text": "Closed on Monday",
            "link": {"url": "https://x.example"},
        }
    )
    assert 'class="announce"><a href="https://x.example">Closed on Monday</a>' in html_of(on)
    off = doc_with(announcement={"enabled": False, "text": "Hidden", "link": None})
    assert "Hidden" not in html_of(off)
    assert 'class="announce"' not in html_of(
        doc_with(announcement={"enabled": True, "text": "", "link": None})
    )


def cover_doc(overlay="dark", transparent=True) -> SiteDocument:
    doc = doc_with(
        header={"style": "classic", "sticky": True, "transparent": transparent, "cta": None}
    )
    hero = doc.pages[0].sections[0]
    hero.variant = "cover"
    hero.props.overlay = overlay
    return doc


def test_transparent_header_only_over_a_cover_hero():
    html = html_of(cover_doc())
    assert "has-overlay-header" in html and "hdr-overlay hdr-tone-light" in html
    assert "has-overlay-header" not in html_of(cover_doc(transparent=False))
    # other pages do not start with a cover hero, so they keep the normal solid header
    assert "has-overlay-header" not in html_of(cover_doc(), "services/index.html")


def test_light_overlay_flips_the_header_text_to_dark():
    assert "hdr-tone-dark" in html_of(cover_doc(overlay="light"))


def test_not_sticky_header():
    assert "hdr-static" in html_of(
        doc_with(header={"style": "classic", "sticky": False, "transparent": False, "cta": None})
    )


def test_logo_replaces_the_name_and_becomes_the_favicon():
    asset = AssetFile("logo.webp", b"logo", width=800, height=200, variants=[(160, b"s")])
    doc = doc_with(
        logo={"asset": "a1", "alt": "Acme", "focus": {"x": 50, "y": 50}}, logo_size="large"
    )
    html = html_of(doc, assets={"a1": asset})
    assert 'class="brand has-logo"' in html and 'aria-label="Northside Studio"' in html
    assert (
        "brand-logo logo-large" in html
        and ">Northside Studio</a>" not in html.split("</header>")[0]
    )
    assert (
        'rel="icon" href="assets/' in html and "-160w.webp" in html
    )  # the small copy, not a data URI


def test_missing_logo_asset_does_not_break_the_page():
    html = html_of(doc_with(logo={"asset": "gone", "alt": "Acme", "focus": {"x": 50, "y": 50}}))
    assert 'class="brand"' in html  # falls back to the text name


@pytest.mark.parametrize("style", ["columns", "centered", "minimal"])
def test_footer_styles(style):
    doc = doc_with(footer={"text": "Thanks", "show_business_info": True, "style": style})
    html = html_of(doc)
    assert f"ftr-{style}" in html and "&copy; Northside Studio" in html
    assert ("ftr-line" in html) == (style == "minimal")
    assert ("<h3>Contact</h3>" in html) == (style != "minimal")


def test_logo_silhouette_rule_exists_for_transparent_headers():
    css = build(doc_with()).files["css/site.css"].decode()
    assert "hdr-tone-light:not(.is-scrolled) .brand-logo{filter:brightness(0) invert(1)}" in css


def test_social_links_render_in_the_contact_section_with_logos_not_in_the_footer():
    business = {
        "social": {"instagram": "https://instagram.com/x", "My Blog": "https://blog.example"}
    }
    data = doc_with(business=business).model_dump(mode="json")
    data["pages"].append(
        {"id": "pg_c", "slug": "c", "title": "Contact", "sections": [{"type": "contact"}]}
    )
    contact = SiteDocument.model_validate(data)
    html = html_of(contact, "c/index.html")
    assert 'class="contact-social"' in html
    assert (
        'href="https://instagram.com/x" rel="noopener" target="_blank" aria-label="Instagram"'
        in html
    )
    assert 'aria-label="My Blog"' in html
    social = html.split('class="contact-social"')[1].split("</ul>")[0]
    assert social.count("<svg") == 2 and "<rect" in social  # Instagram's logo, a globe for the blog
    assert 'class="social"' not in html  # the footer no longer lists them
    assert "contact-social" not in html_of(doc_with(), "index.html")
    with pytest.raises(ValueError):
        doc_with(business={"social": {"x": "javascript:alert(1)"}})


def test_preview_nav_links_carry_their_page_id_but_exports_do_not():
    from sitegen.preview import render_preview

    doc = doc_with()
    page_id = doc.site.nav[0].page
    assert f'data-page-id="{page_id}"' in render_preview(doc, page_id).html
    assert "data-page-id" not in html_of(doc)
