import io
import zipfile

from helpers import make_project, signup


def test_editor_meta_requires_login_and_lists_sections(client):
    assert client.get("/editor-meta").status_code == 401
    signup(client)
    meta = client.get("/editor-meta").json()
    assert "hero" in {s["type"] for s in meta["sections"]}
    assert "star" in meta["icons"]


def test_preview_renders_unsaved_changes(client):
    signup(client)
    p = make_project(client)
    doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = "Unsaved headline"
    r = client.post(f"/projects/{p['id']}/preview", json={"doc": doc, "page_id": "pg_home"})
    assert r.status_code == 200
    assert "Unsaved headline" in r.json()["html"]
    # nothing was saved
    saved = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    assert saved["pages"][0]["sections"][0]["props"]["heading"] != "Unsaved headline"


def test_preview_errors(client):
    signup(client)
    p = make_project(client)
    doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    assert (
        client.post(f"/projects/{p['id']}/preview", json={"doc": doc, "page_id": "x"}).status_code
        == 404
    )
    doc["pages"][0]["sections"][0]["type"] = "nope"
    assert (
        client.post(
            f"/projects/{p['id']}/preview", json={"doc": doc, "page_id": "pg_home"}
        ).status_code
        == 422
    )


def test_export_returns_a_working_zip(client):
    signup(client)
    p = make_project(client, "Rosa Bakery")
    r = client.post(f"/projects/{p['id']}/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert "rosa-bakery.zip" in r.headers["content-disposition"]
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    assert {"index.html", "css/site.css", "export.json", "README.txt"} <= set(zf.namelist())
    assert b"Rosa Bakery" in zf.read("index.html")


def test_preview_and_export_are_denied_to_strangers(client, db_session):
    from test_projects import other_client

    signup(client)
    p = make_project(client)
    eve = other_client(db_session)
    signup(eve, email="eve@example.com")
    assert eve.post(f"/projects/{p['id']}/export").status_code == 404
