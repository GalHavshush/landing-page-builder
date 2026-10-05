import pytest
from sitegen import SiteDocument, build
from sitegen.sections import REGISTRY, create_section


def doc_with(section) -> SiteDocument:
    return SiteDocument.model_validate(
        {
            "site": {"name": "T"},
            "pages": [{"id": "pg_a", "title": "A", "sections": [section.model_dump(mode="json")]}],
        }
    )


@pytest.mark.parametrize("section_type", sorted(REGISTRY))
def test_every_section_renders_with_defaults(section_type):
    result = build(doc_with(create_section(section_type)))
    html = result.files["index.html"].decode()
    assert f"s-{section_type}" in html
    assert not [i for i in result.issues if i.level == "warning" and "base_url" not in i.message]


@pytest.mark.parametrize("section_type", sorted(REGISTRY))
def test_every_section_variant_renders(section_type):
    section = create_section(section_type)
    variants = type(section).model_fields["variant"].annotation.__args__
    for variant in variants:
        section.variant = variant
        assert (
            f"s-{section_type}--{variant}" in build(doc_with(section)).files["index.html"].decode()
        )


def test_user_text_is_escaped():
    section = create_section("features")
    section.props.items[0].title = "<img src=x onerror=alert(1)>"
    html = build(doc_with(section)).files["index.html"].decode()
    assert "<img src=x" not in html
    assert "&lt;img src=x" in html


def test_every_prop_declares_group_and_control():
    for definition in REGISTRY.values():
        for name, info in definition.props_model.model_fields.items():
            meta = info.json_schema_extra or {}
            assert meta.get("group") in {"content", "design"}, f"{definition.type}.{name}"
            assert meta.get("control"), f"{definition.type}.{name}"


def test_nested_item_fields_declare_a_control():
    """Repeater items are edited from the schema, so every item field needs an editor hint."""
    for definition in REGISTRY.values():
        for name, item in definition.props_model.model_json_schema().get("$defs", {}).items():
            if name in {"Link", "ImageRef"}:  # edited as a whole by dedicated controls
                continue
            for prop, schema in item["properties"].items():
                assert schema.get("control"), f"{definition.type}: {name}.{prop}"
