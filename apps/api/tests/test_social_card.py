import io

from app.projects.social_card import social_card
from PIL import Image
from sitegen.starters import load_starter


def test_card_is_a_1200x630_png_in_brand_colour():
    doc = load_starter("clean")
    img = Image.open(io.BytesIO(social_card(doc)))
    assert img.size == (1200, 630) and img.format == "PNG"
    assert img.getpixel((5, 5)) == (0x25, 0x63, 0xEB)  # the primary colour


def test_long_names_do_not_crash():
    doc = load_starter("clean")
    doc.site.name = "An Extraordinarily Long Business Name " * 8
    doc.site.tagline = "word " * 100
    assert Image.open(io.BytesIO(social_card(doc))).size == (1200, 630)


def test_export_includes_card_only_with_base_url_and_no_chosen_image(client):
    from helpers import export_zip, make_project, signup

    signup(client)
    project = make_project(client)
    pid = project["id"]
    _, zf = export_zip(client, pid)
    assert "social-card.png" not in zf.namelist()  # no base_url: nothing to point at

    got = client.get(f"/projects/{pid}/doc").json()
    doc = got["doc"]
    doc["site"]["base_url"] = "https://example.com"
    assert (
        client.put(
            f"/projects/{pid}/doc", json={"doc": doc, "base_revision": got["revision"]}
        ).status_code
        == 200
    )
    _, zf = export_zip(client, pid)
    assert "social-card.png" in zf.namelist()
    assert "https://example.com/social-card.png" in zf.read("index.html").decode()
