import pytest
from app.exports.routes import KEEP_LAST
from helpers import export_zip, make_project, signup
from test_projects import other_client


@pytest.fixture
def project(client):
    signup(client)
    return make_project(client)


def test_export_records_revision_size_and_warnings(client, project):
    pid = project["id"]
    export, zf = export_zip(client, pid)
    assert export["doc_revision"] == 1 and export["size_bytes"] > 1000
    assert export["created_by"] == "Rosa"
    # the starter has no base_url, so the builder warns about sitemap/canonical
    assert any("base_url" in i["message"] for i in export["issues"])
    assert "index.html" in zf.namelist()


def test_history_lists_newest_first_and_each_is_downloadable(client, project):
    pid = project["id"]
    first, _ = export_zip(client, pid)
    got = client.get(f"/projects/{pid}/doc").json()
    doc = got["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = "Second version"
    client.put(f"/projects/{pid}/doc", json={"doc": doc, "base_revision": got["revision"]})
    second, zf2 = export_zip(client, pid)
    history = client.get(f"/projects/{pid}/exports").json()
    assert [e["id"] for e in history] == [second["id"], first["id"]]
    assert second["doc_revision"] == 2
    assert b"Second version" in zf2.read("index.html")
    # the older export still contains the older text (a rollback source)
    old = client.get(f"/projects/{pid}/exports/{first['id']}/download")
    assert old.status_code == 200 and b"Second version" not in old.content


def test_old_exports_are_pruned(client, project, storage):
    pid = project["id"]
    ids = [export_zip(client, pid)[0]["id"] for _ in range(KEEP_LAST + 2)]
    history = [e["id"] for e in client.get(f"/projects/{pid}/exports").json()]
    assert history == ids[::-1][:KEEP_LAST]
    assert client.get(f"/projects/{pid}/exports/{ids[0]}/download").status_code == 404
    # artifact files are deleted too, not just rows
    assert len(list((storage.root / "exports").rglob("*.zip"))) == KEEP_LAST


def test_exports_are_private_to_the_project(client, project, db_session):
    pid = project["id"]
    export, _ = export_zip(client, pid)
    eve = other_client(db_session)
    signup(eve, email="eve@example.com")
    other = make_project(eve)
    assert eve.get(f"/projects/{pid}/exports").status_code == 404
    assert eve.get(f"/projects/{pid}/exports/{export['id']}/download").status_code == 404
    # a member of another project cannot fetch this export through their own project id either
    assert eve.get(f"/projects/{other['id']}/exports/{export['id']}/download").status_code == 404


def test_download_needs_login(client, project):
    export, _ = export_zip(client, project["id"])
    client.cookies.clear()
    assert (
        client.get(f"/projects/{project['id']}/exports/{export['id']}/download").status_code == 401
    )
