from datetime import timedelta

from app.auth.models import UserSession
from app.config import get_settings
from app.db import utcnow

CREDS = {"email": "Rosa@Example.com", "password": "correct horse", "name": "Rosa"}


def register(client, **overrides):
    return client.post("/auth/register", json={**CREDS, **overrides})


def test_register_logs_in_and_normalises_email(client):
    r = register(client)
    assert r.status_code == 201
    assert r.json()["email"] == "rosa@example.com"
    assert "password" not in r.text
    assert client.get("/auth/me").json()["name"] == "Rosa"


def test_session_cookie_is_httponly_and_samesite(client):
    cookie = register(client).headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_token_is_stored_hashed(client, db_session):
    register(client)
    token = client.cookies["session"]
    stored = db_session.query(UserSession).one()
    assert stored.token_hash != token and len(stored.token_hash) == 64


def test_duplicate_email_conflicts(client):
    register(client)
    assert register(client, email="rosa@example.com").status_code == 409


def test_short_password_rejected(client):
    assert register(client, password="short").status_code == 422


def test_login_logout_flow(client):
    register(client)
    client.post("/auth/logout")
    assert client.get("/auth/me").status_code == 401
    assert client.post("/auth/login", json=CREDS | {"email": "rosa@example.com"}).status_code == 200
    assert client.get("/auth/me").status_code == 200
    client.post("/auth/logout")
    assert client.get("/auth/me").status_code == 401


def test_logout_invalidates_the_token_server_side(client):
    register(client)
    token = client.cookies["session"]
    client.post("/auth/logout")
    client.cookies.set("session", token)
    assert client.get("/auth/me").status_code == 401


def test_wrong_password_and_unknown_user_look_the_same(client):
    register(client)
    wrong = client.post("/auth/login", json={"email": "rosa@example.com", "password": "nope nope"})
    unknown = client.post("/auth/login", json={"email": "x@example.com", "password": "nope nope"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_expired_session_is_rejected(client, db_session):
    register(client)
    row = db_session.query(UserSession).one()
    row.expires_at = utcnow() - timedelta(seconds=1)
    db_session.commit()
    assert client.get("/auth/me").status_code == 401


def test_unsafe_requests_need_the_csrf_header(client):
    client.headers.pop("X-Requested-With")
    assert register(client).status_code == 403
    assert client.get("/health").status_code == 200


def test_registration_can_be_closed(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "allow_registration", False)
    assert register(client).status_code == 403
