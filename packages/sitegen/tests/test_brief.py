import pytest
from pydantic import ValidationError
from sitegen import build
from sitegen.brief import STARTER_FOR_TYPE, Brief, build_document

FULL = {
    "name": "Rosa's Bakery",
    "tagline": "Bread worth waking up for",
    "description": "A neighbourhood bakery.",
    "business_type": "local_shop",
    "goal": {"kind": "call"},
    "business": {
        "phone": "+972 50 123 4567",
        "email": "rosa@example.com",
        "address": "Dizengoff 1",
    },
    "pages": ["about", "services", "pricing", "team", "faq"],
    "palette": {"primary": "#B4532A"},
    "headline": "Fresh every morning",
    "highlights": [{"title": "Slow dough", "text": "36 hours."}, {}],
    "stats": [{"value": "10+", "label": "Years"}],
    "testimonials": [{"quote": "Great!", "author": "Dana"}],
    "story": "We started in 2015.",
    "services": [{"title": "Sourdough", "description": "Daily", "price": "28"}],
    "plans": [{"name": "Box", "price": "99", "period": "month", "features": "A\nB"}],
    "team": [{"name": "Rosa", "role": "Baker"}],
    "faq": [{"question": "Delivery?", "answer": "Yes."}],
}


def sections(doc, page_id):
    page = next(p for p in doc.pages if p.id == page_id)
    return {s.type: s for s in page.sections}


def test_answers_land_in_the_document():
    doc = build_document(Brief.model_validate(FULL))
    assert doc.site.name == "Rosa's Bakery"
    assert doc.site.business.phone == "+972 50 123 4567"
    assert doc.theme.palette["primary"] == "#B4532A"
    assert [p.slug for p in doc.pages] == [
        "",
        "about",
        "services",
        "pricing",
        "team",
        "faq",
        "contact",
    ]
    assert [n.page for n in doc.site.nav] == [p.id for p in doc.pages]
    home = sections(doc, "pg_home")
    assert home["hero"].props.heading == "Fresh every morning"
    assert home["hero"].props.buttons[0].href.url == "tel:+972501234567"
    assert doc.site.header.cta.href.url == "tel:+972501234567"
    assert [i.title for i in home["features"].props.items] == ["Slow dough"]  # blank item dropped
    assert home["stats"].props.items[0].value == "10+"
    assert home["testimonials"].props.items[0].author == "Dana"
    assert sections(doc, "pg_about")["text"].props.body == "We started in 2015."
    assert sections(doc, "pg_services")["services"].props.items[0].price == "28"
    assert sections(doc, "pg_pricing")["pricing"].props.plans[0].name == "Box"
    assert sections(doc, "pg_team")["team"].props.items[0].name == "Rosa"
    assert sections(doc, "pg_faq")["faq"].props.items[0].question == "Delivery?"
    assert "map" in sections(doc, "pg_contact")
    assert build(doc).files["index.html"]


def test_blank_answers_keep_placeholders_and_skip_optional_sections():
    doc = build_document(Brief(name="X", pages=["services"]))
    home = sections(doc, "pg_home")
    assert set(home) == {"hero", "cta"}  # no invented stats or testimonials
    assert sections(doc, "pg_services")["services"].props.items  # placeholder services stay
    assert "map" not in sections(doc, "pg_contact")  # no address
    assert doc.pages[0].sections[0].props.buttons[0].href.page == "pg_contact"  # call w/o phone


def test_booking_goal_links_out():
    doc = build_document(Brief(name="X", goal={"kind": "book", "url": "https://cal.example.com/x"}))
    assert doc.pages[0].sections[0].props.buttons[0].href.url == "https://cal.example.com/x"


@pytest.mark.parametrize("business_type", sorted(STARTER_FOR_TYPE))
@pytest.mark.parametrize("language", ["en", "he"])
def test_every_business_type_builds_in_both_languages(business_type, language):
    doc = build_document(
        Brief.model_validate({**FULL, "business_type": business_type, "language": language})
    )
    assert doc.site.default_language == language
    assert "index.html" in build(doc).files
    if language == "he":
        assert doc.pages[0].title == "בית"
        assert doc.pages[-1].title == "יצירת קשר"
        assert all(f in {"heebo", "rubik"} for f in doc.theme.fonts.values())


def test_extra_languages_and_template_override():
    doc = build_document(
        Brief(name="X", language="he", extra_languages=["en", "he"], template="gym")
    )
    assert doc.site.languages == ["he", "en"]
    assert doc.theme.palette["primary"] == "#E4572E"  # the gym starter's colour


def test_bad_palette_is_rejected():
    with pytest.raises(ValidationError):
        Brief(name="X", palette={"primary": "red"})
