"""The content-only guard is security-critical: test what an editor can and cannot change."""

import copy

import pytest
from app.projects.content_guard import content_violations
from sitegen.starters import load_starter


@pytest.fixture
def old() -> dict:
    data = load_starter("clean").model_dump(mode="json")
    data["site"]["languages"] = ["en", "he"]
    return data


def edit(old, fn) -> list[str]:
    new = copy.deepcopy(old)
    fn(new)
    return content_violations(old, new)


def test_unchanged_document_is_fine(old):
    assert content_violations(old, copy.deepcopy(old)) == []


# ---- what a client may change ------------------------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["pages"][0]["sections"][0]["props"].update(heading="New headline"),
        lambda d: d["pages"][0]["sections"][1]["props"]["items"].append(
            {"icon": "star", "title": "New", "text": "Added by client"}
        ),
        lambda d: d["pages"][0]["sections"][1]["props"]["items"].pop(),
        lambda d: d["pages"][0]["sections"][1]["props"]["items"].reverse(),
        lambda d: d["pages"][1]["sections"][0]["props"]["items"][0].update(price="$99"),
        lambda d: d["pages"][0]["sections"][0]["props"]["buttons"][0].update(label="Book now"),
        lambda d: d["site"]["business"].update(phone="+1 555 9999", address="New address"),
        lambda d: d["site"]["business"]["hours"].append(
            {"label": "Sun", "open": "", "close": "", "closed": True}
        ),
        lambda d: d["site"].update(tagline="A new tagline"),
        lambda d: d["site"]["footer"].update(text="Copyright us"),
        lambda d: d["site"]["seo"].update(default_description="Better description"),
        lambda d: d["pages"][0]["seo"].update(description="Page description", title="Custom title"),
        lambda d: d["pages"][0]["sections"][0]["i18n"].update(he={"heading": "שלום"}),
        lambda d: d["site"]["i18n"].update(
            he={
                "name": "ת",
                "tagline": None,
                "description": None,
                "address": None,
                "hours": None,
                "footer_text": None,
            }
        ),
        lambda d: d["pages"][0]["i18n"].update(
            he={"title": None, "slug": None, "seo_title": "כותרת", "seo_description": None}
        ),
    ],
)
def test_content_edits_are_allowed(old, mutate):
    assert edit(old, mutate) == []


# ---- what a client must NOT be able to change ----------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["pages"][0]["sections"].pop(),  # delete a section
        lambda d: d["pages"][0]["sections"].reverse(),  # reorder sections
        lambda d: d["pages"][0]["sections"].append(
            copy.deepcopy(d["pages"][0]["sections"][0]) | {"id": "sec_new"}
        ),
        lambda d: d["pages"].pop(),  # delete a page
        lambda d: d["pages"].append(
            {
                "id": "pg_x",
                "slug": "x",
                "title": "X",
                "seo": {"title": None, "description": None, "social_image": None, "noindex": False},
                "sections": [],
                "i18n": {},
            }
        ),
        lambda d: d["pages"][0]["sections"][0].update(variant="split"),
        lambda d: d["pages"][0]["sections"][0]["style"].update(background="dark"),
        lambda d: d["pages"][0]["sections"][0]["props"].update(
            image_position="start"
        ),  # design prop
        lambda d: d["pages"][0]["sections"][1]["props"].update(columns=2),  # design prop
        lambda d: d["pages"][0]["sections"][0].update(type="text"),  # change type
        lambda d: d["pages"][0]["sections"][0].update(id="sec_other"),  # change id
        lambda d: d["theme"]["palette"].update(primary="#FF0000"),
        lambda d: d["theme"].update(radius="full"),
        lambda d: d["theme"]["fonts"].update(heading="serif"),
        lambda d: d["site"].update(name="Renamed"),
        lambda d: d["site"].update(base_url="https://evil.example"),
        lambda d: d["site"]["nav"].pop(),
        lambda d: d["site"]["nav"][0].update(label="Hacked"),
        lambda d: d["site"]["languages"].append("fr"),
        lambda d: d["site"].update(default_language="he"),
        lambda d: d["site"]["footer"].update(show_business_info=False),
        lambda d: d["pages"][0].update(slug="renamed"),
        lambda d: d["pages"][1].update(title="Renamed page"),
        lambda d: d["pages"][0]["seo"].update(noindex=True),
        lambda d: d["pages"][0]["i18n"].update(
            he={"title": "כותרת", "slug": None, "seo_title": None, "seo_description": None}
        ),
        lambda d: d["pages"][0]["i18n"].update(
            he={"title": None, "slug": "shalom", "seo_title": None, "seo_description": None}
        ),
        lambda d: d.update(schema_version=2),
        lambda d: d.update(extra_top_level_key={"x": 1}),  # unknown keys are locked by default
        lambda d: d["pages"][0]["sections"][0].update(brand_new_field="x"),
    ],
)
def test_structure_and_design_edits_are_rejected(old, mutate):
    violations = edit(old, mutate)
    assert violations, "this change must be rejected for the editor role"


def test_violations_name_where_the_change_was(old):
    v = edit(old, lambda d: d["theme"]["palette"].update(primary="#FF0000"))
    assert v == ["/theme/palette/primary"]
    v = edit(old, lambda d: d["pages"][0]["sections"][0]["style"].update(spacing="compact"))
    assert any("/style/spacing" in p for p in v)


def test_a_mixed_edit_is_rejected_as_a_whole(old):
    def mutate(d):
        d["pages"][0]["sections"][0]["props"]["heading"] = "fine"  # allowed
        d["theme"]["radius"] = "full"  # not allowed

    assert edit(old, mutate) == ["/theme/radius"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["site"]["header"].update(style="split"),
        lambda d: d["site"]["header"].update(transparent=True),
        lambda d: d["site"]["header"].update(
            cta={"label": "Buy", "href": {"url": "https://x.example"}, "style": "primary"}
        ),
        lambda d: d["site"]["announcement"].update(enabled=True, text="Sale"),
        lambda d: d["site"]["footer"].update(style="minimal"),
        lambda d: d["site"].update(logo={"asset": "a1", "alt": "x", "focus": {"x": 50, "y": 50}}),
        lambda d: d["site"].update(logo_size="large"),
    ],
)
def test_branding_and_navigation_chrome_is_not_client_editable(old, mutate):
    assert edit(old, mutate), "header, footer, logo and announcement belong to the designer"


def test_clients_may_translate_the_cta_and_announcement_text(old):
    def mutate(d):
        d["site"]["i18n"]["he"] = {
            "name": None,
            "tagline": None,
            "description": None,
            "address": None,
            "hours": None,
            "footer_text": None,
            "cta_label": "הזמינו",
            "announcement_text": "מבצע",
        }

    assert edit(old, mutate) == []
