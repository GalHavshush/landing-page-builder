import pytest
from app.assets.storage import LocalStorage, S3Storage, StorageNotFound
from app.config import Settings
from moto import mock_aws


def roundtrip(storage):
    storage.put("p1/abc/x.webp", b"data", "image/webp")
    assert storage.get("p1/abc/x.webp") == b"data"
    storage.delete("p1/abc/x.webp")
    with pytest.raises(StorageNotFound):
        storage.get("p1/abc/x.webp")


def test_local_storage(tmp_path):
    roundtrip(LocalStorage(str(tmp_path)))


def test_local_storage_refuses_path_traversal(tmp_path):
    s = LocalStorage(str(tmp_path / "root"))
    with pytest.raises(StorageNotFound):
        s.get("../secret")
    with pytest.raises(ValueError):
        s.put("../../evil", b"x", "text/plain")


@mock_aws
def test_s3_storage_against_mock_s3(monkeypatch):
    settings = Settings(
        s3_bucket="test-bucket", s3_access_key="x", s3_secret_key="y", s3_region="us-east-1"
    )
    s = S3Storage(settings)
    s.client.create_bucket(Bucket="test-bucket")
    roundtrip(s)
