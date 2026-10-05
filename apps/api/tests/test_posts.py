import io
import zipfile

import pytest
from helpers import image_bytes, make_project, signup, upload
from test_projects import other_client


@pytest.fixture
def project(client):
    signup(client)
    return make_project(client)


def new_post(client, pid, **kw):
    body = {"lang": "en", "title": "Hello world", "slug": "hello-world", "body_md": "Some **text**"}
    body.update(kw)
    return client.post(f"/projects/{pid}/posts", json=body)


def publish(client, pid, post, **kw):
    body = {
        "lang": post["lang"],
        "title": post["title"],
        "slug": post["slug"],
        "excerpt": post["excerpt"],
        "body_md": post["body_md"],
        "status": "published",
    }
    body.update(kw)
    return client.put(f"/projects/{pid}/posts/{post['id']}", json=body)


def export_files(client, pid) -> dict[str, bytes]:
    z = zipfile.ZipFile(io.BytesIO(client.post(f"/projects/{pid}/export").content))
    return {n: z.read(n) for n in z.namelist()}


def test_create_list_get_update_delete(client, project):
    pid = project["id"]
    r = new_post(client, pid)
    assert r.status_code == 201
    post = r.json()
    assert post["status"] == "draft" and post["published_at"] is None
    assert post["id"].startswith("post_") and post["translation_group"].startswith("grp_")
    assert [p["id"] for p in client.get(f"/projects/{pid}/posts").json()] == [post["id"]]
    assert client.get(f"/projects/{pid}/posts/{post['id']}").json()["title"] == "Hello world"
    upd = publish(client, pid, post, title="Hello again")
    assert upd.json()["title"] == "Hello again"
    assert upd.json()["published_at"] is not None  # first publish stamps the date
    assert client.delete(f"/projects/{pid}/posts/{post['id']}").status_code == 204
    assert client.get(f"/projects/{pid}/posts").json() == []


@pytest.mark.parametrize("slug", ["Has Caps", "with space", "-lead", "trail-", "a--b", ""])
def test_slug_validation(client, project, slug):
    assert new_post(client, project["id"], slug=slug).status_code == 422


def test_slug_unique_per_language(client, project):
    pid = project["id"]
    assert new_post(client, pid).status_code == 201
    assert new_post(client, pid).status_code == 409


def test_language_must_exist_on_the_site(client, project):
    assert new_post(client, project["id"], lang="fr").status_code == 422


def test_only_published_posts_reach_the_export(client, project):
    pid = project["id"]
    draft = new_post(client, pid, slug="secret-draft", title="Secret draft").json()
    live = new_post(client, pid, slug="live-post", title="Live post").json()
    publish(client, pid, live)
    files = export_files(client, pid)
    assert "blog/live-post/index.html" in files
    assert "blog/secret-draft/index.html" not in files
    assert b"Secret draft" not in b"".join(files.values())
    assert b"Live post" in files["posts.json"] and draft["id"].encode() not in files["posts.json"]
    assert b"<strong>text</strong>" in files["blog/live-post/index.html"]


def test_unpublishing_removes_the_page(client, project):
    pid = project["id"]
    post = new_post(client, pid).json()
    publish(client, pid, post)
    assert "blog/hello-world/index.html" in export_files(client, pid)
    client.put(f"/projects/{pid}/posts/{post['id']}", json={**post, "status": "draft"})
    assert "blog/hello-world/index.html" not in export_files(client, pid)


def test_translate_creates_linked_draft_and_is_exported_with_hreflang(client, project):
    pid = project["id"]
    doc = client.get(f"/projects/{pid}/doc").json()
    d = doc["doc"]
    d["site"]["languages"] = ["en", "he"]
    d["site"]["base_url"] = "https://example.com"
    assert (
        client.put(
            f"/projects/{pid}/doc", json={"doc": d, "base_revision": doc["revision"]}
        ).status_code
        == 200
    )
    en = publish(client, pid, new_post(client, pid).json()).json()
    he = client.post(f"/projects/{pid}/posts/{en['id']}/translate", json={"lang": "he"})
    assert he.status_code == 201
    he = he.json()
    assert he["translation_group"] == en["translation_group"] and he["status"] == "draft"
    assert (
        client.post(f"/projects/{pid}/posts/{en['id']}/translate", json={"lang": "he"}).status_code
        == 409
    )
    client.put(
        f"/projects/{pid}/posts/{he['id']}",
        json={**he, "title": "שלום עולם", "status": "published"},
    )
    files = export_files(client, pid)
    assert "he/blog/hello-world/index.html" in files
    assert b'hreflang="he"' in files["blog/hello-world/index.html"]


def test_cover_and_inline_images_ship_and_block_asset_deletion(client, project):
    pid = project["id"]
    cover = upload(client, pid, image_bytes("PNG", (64, 48)), name="cover.png").json()
    inline = upload(client, pid, image_bytes("PNG", (32, 32)), name="inline.png").json()
    unused = upload(client, pid, image_bytes("PNG", (16, 16)), name="unused.png").json()
    post = new_post(
        client, pid, body_md=f"![pic](asset:{inline['id']})", cover_asset_id=cover["id"]
    ).json()
    publish(client, pid, post, cover_asset_id=cover["id"], body_md=f"![pic](asset:{inline['id']})")
    files = export_files(client, pid)
    shipped = [n for n in files if n.startswith("assets/")]
    assert len(shipped) == 2 and not any("unused" in n for n in shipped)
    assert client.delete(f"/projects/{pid}/assets/{cover['id']}").status_code == 409
    assert client.delete(f"/projects/{pid}/assets/{inline['id']}").status_code == 409
    assert client.delete(f"/projects/{pid}/assets/{unused['id']}").status_code == 204


def test_cover_must_belong_to_the_project(client, project, db_session):
    other = other_client(db_session)
    signup(other, email="eve@example.com")
    foreign = upload(other, make_project(other)["id"], image_bytes()).json()
    assert new_post(client, project["id"], cover_asset_id=foreign["id"]).status_code == 422


def test_preview_renders_unsaved_text(client, project):
    pid = project["id"]
    post = new_post(client, pid).json()
    body = {
        "lang": "en",
        "title": "Draft headline",
        "slug": "hello-world",
        "body_md": "# Big\n\ntext",
        "status": "draft",
    }
    r = client.post(f"/projects/{pid}/posts/{post['id']}/preview", json=body)
    assert r.status_code == 200
    assert "Draft headline" in r.json()["html"] and "<h1>Big</h1>" in r.json()["html"]
    assert (
        client.get(f"/projects/{pid}/posts/{post['id']}").json()["title"] == "Hello world"
    )  # not saved


def test_posts_are_private_to_members(client, project, db_session):
    post = new_post(client, project["id"]).json()
    eve = other_client(db_session)
    signup(eve, email="eve@example.com")
    pid = project["id"]
    assert eve.get(f"/projects/{pid}/posts").status_code == 404
    assert eve.get(f"/projects/{pid}/posts/{post['id']}").status_code == 404
    assert eve.delete(f"/projects/{pid}/posts/{post['id']}").status_code == 404
