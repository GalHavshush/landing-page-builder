import pytest
from sitegen import SiteDocument, build
from sitegen.localize import untranslated
from sitegen.meta import editor_meta
from sitegen.starters import list_starters, load_starter


def english(name: str) -> dict:
    return load_starter(name).model_dump(mode="json")


@pytest.mark.parametrize("name", list_starters())
def test_every_starter_has_complete_hebrew_content(name):
    doc = english(name)
    assert untranslated({"site": doc["site"], "pages": doc["pages"]}, "he") == []
    he = load_starter(name, site_name="האתר שלי", lang="he")
    assert he.site.name == "האתר שלי" and he.pages[0].title != doc["pages"][0]["title"]
    # the language is chosen by the caller; fonts must cover Hebrew so nothing falls back
    for font in he.theme.fonts.values():
        assert font in {"heebo", "rubik"}
    assert build(
        SiteDocument.model_validate(
            {
                **he.model_dump(),
                "site": {**he.site.model_dump(), "default_language": "he", "languages": ["he"]},
            }
        )
    ).files


def test_new_section_and_page_filler_follows_the_language():
    meta = editor_meta()
    assert untranslated([s["template"] for s in meta["sections"]], "he") == []
    assert (
        untranslated(
            [
                {"title": r["title"], "sections": r["sections"]}
                for r in meta["page_recipes"].values()
            ],
            "he",
        )
        == []
    )
    he = editor_meta("he")
    assert he["page_recipes"]["about"]["title"] == "אודותינו"
    assert (
        he["page_recipes"]["about"]["label"] == meta["page_recipes"]["about"]["label"]
    )  # editor text stays


def test_languages_without_a_table_keep_english():
    assert load_starter("clean", lang="fr").pages[0].title == "Home"
    assert load_starter("clean").pages[0].title == "Home"
