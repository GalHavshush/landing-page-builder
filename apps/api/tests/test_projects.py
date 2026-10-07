import copy

from app.main import create_app
from fastapi.testclient import TestClient
from helpers import make_project, signup


def other_client(db_session):
    """A second browser (separate cookie jar) sharing the same database."""
    from app.db import get_db

    app = create_app()

    def override():
        yield db_session
        db_session.commit()

    app.dependency_overrides[get_db] = override
    return TestClient(app, base_url="http://localhost", headers={"X-Requested-With": "builder"})


def test_requires_login(client):
    assert client.get("/projects").status_code == 401
    assert client.post("/projects", json={"name": "x"}).status_code == 401


def test_create_from_template_and_list(client):
    signup(client)
    p = make_project(client, "Rosa Bakery")
    assert p["slug"] == "rosa-bakery" and p["role"] == "owner" and p["revision"] == 1
    assert [x["id"] for x in client.get("/projects").json()] == [p["id"]]
    doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    assert doc["site"]["name"] == "Rosa Bakery"
    assert len(doc["pages"]) == 3


def test_slugs_are_unique(client):
    signup(client)
    assert make_project(client, "Same")["slug"] == "same"
    assert make_project(client, "Same")["slug"] == "same-2"


def test_unknown_template_rejected(client):
    signup(client)
    assert client.post("/projects", json={"name": "x", "template": "nope"}).status_code == 422


def test_save_bumps_revision(client):
    signup(client)
    p = make_project(client)
    got = client.get(f"/projects/{p['id']}/doc").json()
    doc = got["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = "New heading"
    r = client.put(f"/projects/{p['id']}/doc", json={"doc": doc, "base_revision": got["revision"]})
    assert r.status_code == 200 and r.json()["revision"] == 2
    again = client.get(f"/projects/{p['id']}/doc").json()
    assert again["revision"] == 2
    assert again["doc"]["pages"][0]["sections"][0]["props"]["heading"] == "New heading"


def test_stale_save_conflicts_and_changes_nothing(client):
    signup(client)
    p = make_project(client)
    doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    ok = client.put(f"/projects/{p['id']}/doc", json={"doc": doc, "base_revision": 1})
    assert ok.status_code == 200
    stale = copy.deepcopy(doc)
    stale["site"]["name"] = "Stale"
    r = client.put(f"/projects/{p['id']}/doc", json={"doc": stale, "base_revision": 1})
    assert r.status_code == 409
    assert r.json()["detail"]["current_revision"] == 2
    assert client.get(f"/projects/{p['id']}/doc").json()["doc"]["site"]["name"] != "Stale"


def test_invalid_document_is_rejected_with_details(client):
    signup(client)
    p = make_project(client)
    doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = 5
    doc["pages"][1]["sections"][0]["type"] = "carousel"
    r = client.put(f"/projects/{p['id']}/doc", json={"doc": doc, "base_revision": 1})
    assert r.status_code == 422
    assert client.get(f"/projects/{p['id']}/doc").json()["revision"] == 1


def test_other_users_cannot_see_or_touch_projects(client, db_session):
    signup(client)
    p = make_project(client)
    intruder = other_client(db_session)
    signup(intruder, email="eve@example.com")
    assert intruder.get("/projects").json() == []
    assert intruder.get(f"/projects/{p['id']}").status_code == 404
    assert intruder.get(f"/projects/{p['id']}/doc").status_code == 404
    assert intruder.delete(f"/projects/{p['id']}").status_code == 404


def test_rename_and_delete(client):
    signup(client)
    p = make_project(client)
    r = client.patch(f"/projects/{p['id']}", json={"name": "Renamed"})
    assert r.json()["name"] == "Renamed"
    assert client.delete(f"/projects/{p['id']}").status_code == 204
    assert client.get(f"/projects/{p['id']}").status_code == 404


def test_templates_are_described_and_each_one_creates_a_valid_project(client):
    signup(client)
    templates = client.get("/templates").json()
    assert {t["id"] for t in templates} >= {"clean", "warm", "minimal"}
    assert all(t["label"] and t["description"] for t in templates)
    for t in templates:
        p = make_project(client, f"Site {t['id']}", template=t["id"])
        doc = client.get(f"/projects/{p['id']}/doc").json()["doc"]
        assert doc["site"]["name"] == f"Site {t['id']}"
        assert doc["theme"]["template"] == t["id"]
        assert client.post(f"/projects/{p['id']}/exports").status_code == 201


def test_deleting_a_project_removes_everything_including_files(client, storage, db_session):
    from app.assets.models import Asset
    from app.exports.models import SiteExport
    from app.members.models import Invitation
    from app.posts.models import BlogPost
    from helpers import export_zip, image_bytes, upload

    signup(client)
    p = make_project(client)
    keep = make_project(client, "Other site")
    upload(client, p["id"], image_bytes())
    export_zip(client, p["id"])
    client.post(f"/projects/{p['id']}/posts", json={"lang": "en", "title": "T", "slug": "t"})
    client.post(f"/projects/{p['id']}/invitations", json={"role": "editor"})
    upload(client, keep["id"], image_bytes())  # must survive

    assert client.delete(f"/projects/{p['id']}").status_code == 204
    for model in (Asset, SiteExport, BlogPost, Invitation):
        remaining = db_session.query(model).filter(model.project_id == p["id"]).count()
        assert remaining == 0, model.__name__
    files = [f.relative_to(storage.root).parts[0] for f in storage.root.rglob("*") if f.is_file()]
    assert sorted(set(files)) == ["p2"]  # only the other project's upload is left
    assert [x["id"] for x in client.get("/projects").json()] == [keep["id"]]


def test_create_project_in_hebrew_only(client):
    signup(client)
    r = client.post("/projects", json={"name": "Shop", "language": "he"})
    assert r.status_code == 201
    site = client.get(f"/projects/{r.json()['id']}/doc").json()["doc"]["site"]
    assert (site["default_language"], site["languages"]) == ("he", ["he"])
    both = client.post(
        "/projects", json={"name": "Two", "language": "he", "extra_languages": ["en"]}
    )
    assert client.get(f"/projects/{both.json()['id']}/doc").json()["doc"]["site"]["languages"] == [
        "he",
        "en",
    ]
    assert client.post("/projects", json={"name": "X", "language": "zz"}).status_code == 422


def test_hebrew_site_starts_with_hebrew_placeholder_text(client):
    signup(client)
    r = client.post("/projects", json={"name": "Shop", "template": "warm", "language": "he"})
    doc = client.get(f"/projects/{r.json()['id']}/doc").json()["doc"]
    assert doc["pages"][0]["title"] == "בית" and doc["site"]["name"] == "Shop"
    assert (
        client.get("/editor-meta", params={"lang": "he"}).json()["page_recipes"]["about"]["title"]
        == "אודותינו"
    )
    en = client.get("/editor-meta").json()
    assert en["page_recipes"]["about"]["title"] == "About us"
