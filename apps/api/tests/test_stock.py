import httpx
import pytest
from app.stock.provider import PexelsProvider, StockError, StockPhoto
from app.stock.routes import get_stock_provider
from helpers import image_bytes, make_project, signup

JPEG = image_bytes("PNG", (800, 600))


def raw_photo(pid=101, host="images.pexels.com"):
    return {
        "id": pid,
        "width": 800,
        "height": 600,
        "url": f"https://www.pexels.com/photo/{pid}/",
        "photographer": "Jane Doe",
        "alt": "A red bicycle",
        "src": {
            "medium": f"https://{host}/p/{pid}-m.jpg",
            "large": f"https://{host}/p/{pid}-l.jpg",
        },
    }


def provider_with(handler) -> PexelsProvider:
    return PexelsProvider("KEY", client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_search_parses_results_and_sends_key():
    seen = {}

    def handler(request):
        seen["auth"] = request.headers["authorization"]
        seen["q"] = request.url.params["query"]
        return httpx.Response(200, json={"photos": [raw_photo()]})

    photos = provider_with(handler).search("bike")
    assert seen == {"auth": "KEY", "q": "bike"}
    assert photos[0].credit == "Photo by Jane Doe on Pexels" and photos[0].alt == "A red bicycle"


def test_provider_refuses_image_urls_on_other_hosts():
    def handler(request):
        return httpx.Response(200, json={"photos": [raw_photo(host="evil.example.com")]})

    with pytest.raises(StockError):
        provider_with(handler).search("x")


@pytest.mark.parametrize("pid", ["abc", "1/../2", ""])
def test_get_rejects_non_numeric_ids(pid):
    with pytest.raises(StockError):
        provider_with(lambda r: httpx.Response(200, json=raw_photo())).get(pid)


def test_download_is_size_capped(monkeypatch):
    monkeypatch.setattr("app.stock.provider.MAX_DOWNLOAD_BYTES", 10)
    p = provider_with(lambda r: httpx.Response(200, content=b"x" * 100))
    photo = PexelsProvider._photo(raw_photo())
    with pytest.raises(StockError):
        p.download(photo)


def test_download_refuses_unlisted_hosts():
    photo = PexelsProvider._photo(raw_photo())
    photo.full_url = "http://169.254.169.254/latest/meta-data"
    with pytest.raises(StockError):
        provider_with(lambda r: httpx.Response(200, content=b"x")).download(photo)


class FakeProvider:
    name = "fake"

    def search(self, query, page=1):
        return [self.get("101")]

    def get(self, photo_id):
        return StockPhoto(
            photo_id,
            "https://images.pexels.com/t.jpg",
            "https://images.pexels.com/f.jpg",
            800,
            600,
            "A red bicycle",
            "Photo by Jane Doe on Pexels",
            "https://pexels.com/p/1",
        )

    def download(self, photo):
        return JPEG


@pytest.fixture
def project(client):
    signup(client)
    return make_project(client)


@pytest.fixture
def fake_provider(client):
    client.app.dependency_overrides[get_stock_provider] = lambda: FakeProvider()


def test_search_reports_disabled_without_a_key(client, project):
    r = client.get(f"/projects/{project['id']}/stock/search", params={"q": "bike"})
    assert r.status_code == 200 and r.json() == {"enabled": False, "provider": "", "results": []}


def test_import_without_a_key_is_503(client, project):
    r = client.post(f"/projects/{project['id']}/stock/import", json={"photo_id": "1"})
    assert r.status_code == 503


def test_search_and_import_creates_an_asset_with_credit(client, project, fake_provider):
    found = client.get(f"/projects/{project['id']}/stock/search", params={"q": "bike"}).json()
    assert found["enabled"] and found["results"][0]["credit"].startswith("Photo by Jane")
    r = client.post(
        f"/projects/{project['id']}/stock/import", json={"photo_id": found["results"][0]["id"]}
    )
    assert r.status_code == 201
    asset = r.json()
    assert (
        asset["alt_default"] == "A red bicycle" and asset["credit"] == "Photo by Jane Doe on Pexels"
    )
    listed = client.get(f"/projects/{project['id']}/assets").json()
    assert [a["id"] for a in listed] == [asset["id"]]


@pytest.mark.parametrize("bad", ["http://evil.test/x.jpg", "../1", "12a", ""])
def test_import_only_accepts_numeric_ids_never_urls(client, project, fake_provider, bad):
    r = client.post(f"/projects/{project['id']}/stock/import", json={"photo_id": bad})
    assert r.status_code == 422


def test_stock_requires_edit_access(client, project, fake_provider):
    client.cookies.clear()
    assert (
        client.get(f"/projects/{project['id']}/stock/search", params={"q": "x"}).status_code == 401
    )
