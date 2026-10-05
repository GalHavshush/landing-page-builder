import copy
from datetime import timedelta

import pytest
from app.db import utcnow
from app.members.models import Invitation
from helpers import image_bytes, make_project, signup, upload
from test_projects import other_client


@pytest.fixture
def project(client):
    signup(client)  # rosa, the owner (the agency)
    return make_project(client)


def invite(client, pid, role="editor", **kw):
    r = client.post(f"/projects/{pid}/invitations", json={"role": role, **kw})
    assert r.status_code == 201, r.text
    return r.json()


def join(db_session, token, email, role_name="Client"):
    """A second person signs up and accepts an invite link."""
    c = other_client(db_session)
    signup(c, email=email, name=role_name)
    r = c.post(f"/invitations/{token}/accept")
    assert r.status_code == 200, r.text
    return c


@pytest.fixture
def designer(client, project, db_session):
    return join(db_session, invite(client, project["id"], "designer")["token"], "dee@example.com")


@pytest.fixture
def editor(client, project, db_session):
    return join(db_session, invite(client, project["id"], "editor")["token"], "cleo@example.com")


def get_doc(c, pid):
    return c.get(f"/projects/{pid}/doc").json()


def put_doc(c, pid, doc, rev):
    return c.put(f"/projects/{pid}/doc", json={"doc": doc, "base_revision": rev})


# ---- invitations --------------------------------------------------------------------------


def test_invite_flow_gives_the_invited_role(client, project, db_session):
    inv = invite(client, project["id"], "editor")
    c = other_client(db_session)
    signup(c, email="cleo@example.com")
    preview = c.get(f"/invitations/{inv['token']}").json()
    assert preview["project_name"] == "Rosa Bakery" and preview["role"] == "editor"
    assert c.post(f"/invitations/{inv['token']}/accept").json()["role"] == "editor"
    mine = c.get("/projects").json()
    assert [(p["id"], p["role"]) for p in mine] == [(project["id"], "editor")]


def test_invite_links_are_single_use(client, project, db_session):
    token = invite(client, project["id"])["token"]
    join(db_session, token, "a@example.com")
    c2 = other_client(db_session)
    signup(c2, email="b@example.com")
    assert c2.post(f"/invitations/{token}/accept").status_code == 404


def test_token_is_stored_hashed(client, project, db_session):
    token = invite(client, project["id"])["token"]
    assert db_session.query(Invitation).one().token_hash != token


def test_expired_and_revoked_invites_do_not_work(client, project, db_session):
    token = invite(client, project["id"])["token"]
    row = db_session.query(Invitation).one()
    row.expires_at = utcnow() - timedelta(seconds=1)
    db_session.commit()
    c = other_client(db_session)
    signup(c, email="x@example.com")
    assert c.post(f"/invitations/{token}/accept").status_code == 404
    inv2 = invite(client, project["id"])
    client.delete(f"/projects/{project['id']}/invitations/{inv2['id']}")
    assert c.post(f"/invitations/{inv2['token']}/accept").status_code == 404


def test_email_locked_invite_only_works_for_that_account(client, project, db_session):
    token = invite(client, project["id"], email="Cleo@Example.com")["token"]
    wrong = other_client(db_session)
    signup(wrong, email="mallory@example.com")
    assert wrong.post(f"/invitations/{token}/accept").status_code == 403
    right = other_client(db_session)
    signup(right, email="cleo@example.com")
    assert right.post(f"/invitations/{token}/accept").status_code == 200


def test_accepting_requires_login_and_unknown_tokens_404(client, project, db_session):
    token = invite(client, project["id"])["token"]
    anon = other_client(db_session)
    assert anon.post(f"/invitations/{token}/accept").status_code == 401
    signup(anon, email="y@example.com")
    assert anon.post("/invitations/not-a-token/accept").status_code == 404


def test_owners_cannot_be_invited_and_existing_members_get_409(client, project, db_session):
    assert (
        client.post(f"/projects/{project['id']}/invitations", json={"role": "owner"}).status_code
        == 422
    )
    token = invite(client, project["id"])["token"]
    assert client.post(f"/invitations/{token}/accept").status_code == 409  # rosa already owns it


def test_member_management(client, project, editor):
    pid = project["id"]
    data = client.get(f"/projects/{pid}/members").json()
    roles = {m["email"]: m["role"] for m in data["members"]}
    assert roles == {"rosa@example.com": "owner", "cleo@example.com": "editor"}
    cleo = next(m for m in data["members"] if m["role"] == "editor")
    assert (
        client.patch(
            f"/projects/{pid}/members/{cleo['user_id']}", json={"role": "designer"}
        ).json()["role"]
        == "designer"
    )
    owner = next(m for m in data["members"] if m["role"] == "owner")
    assert client.delete(f"/projects/{pid}/members/{owner['user_id']}").status_code == 409
    assert (
        client.patch(
            f"/projects/{pid}/members/{owner['user_id']}", json={"role": "editor"}
        ).status_code
        == 409
    )
    assert client.delete(f"/projects/{pid}/members/{cleo['user_id']}").status_code == 204
    assert editor.get(f"/projects/{pid}").status_code == 404  # access is gone immediately


# ---- what each role may do ----------------------------------------------------------------


def test_only_owners_manage_members(client, project, designer, editor):
    pid = project["id"]
    for c in (designer, editor):
        assert c.get(f"/projects/{pid}/members").status_code == 403
        assert c.post(f"/projects/{pid}/invitations", json={"role": "editor"}).status_code == 403
        assert c.delete(f"/projects/{pid}").status_code == 403
    assert editor.patch(f"/projects/{pid}", json={"name": "Hax"}).status_code == 403
    assert designer.patch(f"/projects/{pid}", json={"name": "Renamed"}).status_code == 200


def test_designer_can_change_structure_and_design(client, project, designer):
    pid = project["id"]
    got = get_doc(designer, pid)
    doc = got["doc"]
    doc["theme"]["radius"] = "full"
    doc["pages"][0]["sections"].reverse()
    assert put_doc(designer, pid, doc, got["revision"]).status_code == 200


def test_editor_can_change_content(client, project, editor):
    pid = project["id"]
    got = get_doc(editor, pid)
    doc = got["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = "Updated by the client"
    doc["site"]["business"]["phone"] = "+1 555 4321"
    doc["pages"][1]["sections"][0]["props"]["items"][0]["price"] = "$75"
    r = put_doc(editor, pid, doc, got["revision"])
    assert r.status_code == 200, r.text
    saved = get_doc(client, pid)["doc"]
    assert saved["pages"][0]["sections"][0]["props"]["heading"] == "Updated by the client"
    assert saved["pages"][1]["sections"][0]["props"]["items"][0]["price"] == "$75"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["theme"]["palette"].update(primary="#FF0000"),
        lambda d: d["pages"][0]["sections"].pop(),
        lambda d: d["pages"][0]["sections"][0]["style"].update(background="dark"),
        lambda d: d["site"]["nav"].pop(),
        lambda d: (d["pages"].pop(), d["site"]["nav"].pop()),  # a *valid* document without a page
    ],
)
def test_editor_cannot_change_structure_or_design_and_nothing_is_saved(
    client, project, editor, mutate
):
    pid = project["id"]
    got = get_doc(editor, pid)
    original = copy.deepcopy(got)
    doc = got["doc"]
    mutate(doc)
    r = put_doc(editor, pid, doc, got["revision"])
    assert r.status_code == 403
    assert "paths" in r.json()["detail"]
    after = get_doc(client, pid)
    assert after == original  # neither revision nor content changed


def test_editor_mixed_edit_is_rejected_entirely(client, project, editor):
    pid = project["id"]
    got = get_doc(editor, pid)
    doc = got["doc"]
    doc["pages"][0]["sections"][0]["props"]["heading"] = "allowed part"
    doc["theme"]["radius"] = "full"  # forbidden part
    assert put_doc(editor, pid, doc, got["revision"]).status_code == 403
    assert (
        get_doc(client, pid)["doc"]["pages"][0]["sections"][0]["props"]["heading"] != "allowed part"
    )


def test_editor_can_use_media_posts_preview_and_export(client, project, editor):
    pid = project["id"]
    asset = upload(editor, pid, image_bytes()).json()
    assert editor.get(f"/projects/{pid}/assets").status_code == 200
    post = editor.post(
        f"/projects/{pid}/posts", json={"lang": "en", "title": "News", "slug": "news"}
    )
    assert post.status_code == 201
    doc = get_doc(editor, pid)["doc"]
    assert (
        editor.post(f"/projects/{pid}/preview", json={"doc": doc, "page_id": "pg_home"}).status_code
        == 200
    )
    assert editor.post(f"/projects/{pid}/exports").status_code == 201
    assert editor.delete(f"/projects/{pid}/assets/{asset['id']}").status_code == 204


def test_project_lists_show_each_users_role(client, project, designer, editor):
    assert client.get("/projects").json()[0]["role"] == "owner"
    assert designer.get("/projects").json()[0]["role"] == "designer"
    assert editor.get("/projects").json()[0]["role"] == "editor"


def test_roles_do_not_leak_between_projects(client, project, editor):
    other = make_project(client, "Second site")
    assert editor.get(f"/projects/{other['id']}").status_code == 404
    assert editor.get(f"/projects/{other['id']}/doc").status_code == 404
