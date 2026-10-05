import pytest
from helpers import export_zip, image_bytes, make_project, signup, upload
from test_projects import other_client

PNG = image_bytes("PNG", (64, 48))


@pytest.fixture
def project(client):
    signup(client)
    return make_project(client)


def test_upload_returns_urls_and_dimensions(client, project):
    r = upload(client, project["id"], PNG, name="My Photo (1).PNG")
    assert r.status_code == 201
    body = r.json()
    assert body["id"].startswith("asset_")
    assert (body["width"], body["height"]) == (64, 48)
    assert body["filename"] == "My-Photo-1.webp"  # sanitised, extension reflects real format
    assert body["url"].startswith("/api/media/p")
    assert body[
        "thumb_url"
    ]  # tiny pictures have no smaller copy, so the thumbnail is the file itself


def test_uploaded_files_are_served_publicly_as_webp(client, project):
    body = upload(client, project["id"], PNG).json()
    key = body["url"].removeprefix("/api/media/")
    client.cookies.clear()  # public: no login needed
    r = client.get(f"/media/{key}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/webp"
    assert "immutable" in r.headers["cache-control"]
    assert r.headers["x-content-type-options"] == "nosniff"
    assert client.get("/media/p1/does-not-exist.webp").status_code == 404
    assert client.get("/media/../../etc/passwd").status_code in (404, 422)


@pytest.mark.parametrize(
    ("data", "status"),
    [(b"nope", 422), (b"<svg></svg>", 422), (image_bytes("GIF", mode="RGB"), 422)],
)
def test_bad_uploads_are_rejected(client, project, data, status):
    assert upload(client, project["id"], data, name="x.png").status_code == status


def test_oversized_upload_is_rejected(client, project, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "max_upload_bytes", 100)
    assert upload(client, project["id"], PNG).status_code == 413


def test_library_lists_project_assets_newest_first(client, project):
    a = upload(client, project["id"], PNG, name="a.png").json()
    b = upload(client, project["id"], PNG, name="b.png").json()
    listed = client.get(f"/projects/{project['id']}/assets").json()
    assert {x["id"] for x in listed} == {a["id"], b["id"]}


def test_default_alt_text_can_be_set(client, project):
    a = upload(client, project["id"], PNG).json()
    r = client.patch(f"/projects/{project['id']}/assets/{a['id']}", json={"alt_default": "A loaf"})
    assert r.json()["alt_default"] == "A loaf"


def test_delete_unused_asset_removes_files(client, project, storage):
    a = upload(client, project["id"], PNG).json()
    key = a["url"].removeprefix("/api/media/")
    assert client.delete(f"/projects/{project['id']}/assets/{a['id']}").status_code == 204
    assert client.get(f"/media/{key}").status_code == 404
    assert client.get(f"/projects/{project['id']}/assets").json() == []


def use_image(client, project_id, asset_id):
    got = client.get(f"/projects/{project_id}/doc").json()
    doc = got["doc"]
    hero = doc["pages"][0]["sections"][0]
    hero["variant"] = "split"
    hero["props"]["image"] = {"asset": asset_id, "alt": "Fresh loaves"}
    r = client.put(
        f"/projects/{project_id}/doc", json={"doc": doc, "base_revision": got["revision"]}
    )
    assert r.status_code == 200, r.text


def test_cannot_delete_an_asset_that_is_in_use(client, project):
    a = upload(client, project["id"], PNG).json()
    use_image(client, project["id"], a["id"])
    assert client.delete(f"/projects/{project['id']}/assets/{a['id']}").status_code == 409


def test_export_ships_used_images_only(client, project):
    used = upload(client, project["id"], PNG, name="used.png").json()
    upload(client, project["id"], PNG, name="unused.png")
    use_image(client, project["id"], used["id"])
    _, z = export_zip(client, project["id"])
    assets = [n for n in z.namelist() if n.startswith("assets/")]
    assert len(assets) == 1 and assets[0].endswith("used.webp")
    html = z.read("index.html").decode()
    assert f'src="{assets[0]}"' in html and 'alt="Fresh loaves"' in html
    assert 'width="64" height="48"' in html


def test_preview_points_images_at_media_urls(client, project):
    a = upload(client, project["id"], PNG).json()
    use_image(client, project["id"], a["id"])
    doc = client.get(f"/projects/{project['id']}/doc").json()["doc"]
    html = client.post(
        f"/projects/{project['id']}/preview", json={"doc": doc, "page_id": "pg_home"}
    ).json()["html"]
    assert a["url"] in html


def test_other_users_cannot_use_the_library(client, project, db_session):
    a = upload(client, project["id"], PNG).json()
    eve = other_client(db_session)
    signup(eve, email="eve@example.com")
    assert upload(eve, project["id"], PNG).status_code == 404
    assert eve.get(f"/projects/{project['id']}/assets").status_code == 404
    assert eve.delete(f"/projects/{project['id']}/assets/{a['id']}").status_code == 404


def test_exports_include_srcset_variants_and_placeholder_colour(client, project):
    big = image_bytes("JPEG", (2000, 1000), mode="RGB")
    a = upload(client, project["id"], big, name="wide.jpg", content_type="image/jpeg").json()
    use_image(client, project["id"], a["id"])
    _, z = export_zip(client, project["id"])
    names = z.namelist()
    assert any(n.endswith("-320w.webp") for n in names) and any(
        n.endswith("-960w.webp") for n in names
    )
    html = z.read("index.html").decode()
    assert " 320w," in html and " 2000w" in html and "background-color:#" in html


def test_deleting_an_asset_removes_every_variant_file(client, project, storage):
    a = upload(
        client,
        project["id"],
        image_bytes("JPEG", (2000, 1000), mode="RGB"),
        name="w.jpg",
        content_type="image/jpeg",
    ).json()
    before = [f for f in storage.root.rglob("*") if f.is_file()]
    assert len(before) == 5  # main + 320/640/960/1440
    assert client.delete(f"/projects/{project['id']}/assets/{a['id']}").status_code == 204
    assert [f for f in storage.root.rglob("*") if f.is_file()] == []
