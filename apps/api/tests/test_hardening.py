from app.config import get_settings
from app.main import create_app
from app.ratelimit import RateLimiter, login_limiter, register_limiter
from fastapi.testclient import TestClient
from helpers import signup


def test_limiter_blocks_after_the_limit_and_recovers(monkeypatch):
    limiter = RateLimiter(max_attempts=3, window_seconds=60)
    clock = {"t": 1000.0}
    monkeypatch.setattr("app.ratelimit.time.monotonic", lambda: clock["t"])
    for _ in range(3):
        limiter.check("ip")
    try:
        limiter.check("ip")
        raise AssertionError("expected a 429")
    except Exception as exc:
        assert exc.status_code == 429 and int(exc.headers["Retry-After"]) > 0
    limiter.check("someone-else")  # other keys are unaffected
    clock["t"] += 61
    limiter.check("ip")  # window passed


def test_login_is_rate_limited_per_ip(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", True)
    login_limiter.reset()
    codes = [
        client.post(
            "/auth/login", json={"email": "a@example.com", "password": "wrong-password"}
        ).status_code
        for _ in range(17)
    ]
    assert codes[:15] == [401] * 15
    assert codes[15:] == [429, 429]


def test_registration_is_rate_limited(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", True)
    register_limiter.reset()
    codes = [
        client.post(
            "/auth/register", json={"email": f"u{i}@example.com", "password": "long enough"}
        ).status_code
        for i in range(10)
    ]
    assert codes[:8] == [201] * 8 and codes[8:] == [429, 429]


def test_security_headers_and_request_id(client):
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "same-origin"
    assert len(r.headers["x-request-id"]) >= 8
    r2 = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert r2.headers["x-request-id"] == "abc123"


def test_unhandled_errors_do_not_leak_details(db_session):
    app = create_app()

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/boom")
    assert r.status_code == 500
    assert "secret internal detail" not in r.text
    assert r.json()["request_id"] == r.headers["x-request-id"]


def test_signup_still_works_with_limits_disabled(client):
    signup(client)
