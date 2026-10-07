import pytest
from pydantic import ValidationError
from sitegen import SiteDocument

from tests.conftest import basic_doc_data


def test_valid_document_roundtrips(basic_doc):
    again = SiteDocument.model_validate(basic_doc.model_dump())
    assert again == basic_doc


def test_unknown_keys_are_rejected():
    data = basic_doc_data()
    data["pages"][0]["sections"][0]["props"]["colour"] = "red"
    with pytest.raises(ValidationError):
        SiteDocument.model_validate(data)


def test_unknown_section_type_is_rejected():
    data = basic_doc_data()
    data["pages"][0]["sections"][0] = {"type": "carousel"}
    with pytest.raises(ValidationError):
        SiteDocument.model_validate(data)


def test_javascript_urls_are_rejected():
    data = basic_doc_data()
    data["pages"][0]["sections"][0]["props"]["buttons"][0]["href"] = {"url": "javascript:alert(1)"}
    with pytest.raises(ValidationError):
        SiteDocument.model_validate(data)


def test_duplicate_ids_are_rejected():
    data = basic_doc_data()
    data["pages"][0]["sections"][1]["id"] = "sec_hero"
    with pytest.raises(ValidationError, match="duplicate id"):
        SiteDocument.model_validate(data)


def test_design_props_are_not_translatable():
    data = basic_doc_data()
    data["site"]["languages"] = ["en", "he"]
    data["pages"][0]["sections"][0]["i18n"] = {"he": {"image_position": "start"}}
    with pytest.raises(ValidationError, match="not translatable"):
        SiteDocument.model_validate(data)


def test_seo_texts_have_sane_length_limits():
    import pytest
    from pydantic import ValidationError
    from sitegen.schema import SEO, SiteSEO

    assert SEO(title="t" * 200, description="d" * 500)
    with pytest.raises(ValidationError):
        SEO(title="t" * 201)
    with pytest.raises(ValidationError):
        SEO(description="d" * 501)
    with pytest.raises(ValidationError):
        SiteSEO(default_description="d" * 501)
