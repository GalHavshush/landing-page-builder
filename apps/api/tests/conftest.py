import pytest
from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.assets.storage import LocalStorage, get_storage
from app.db import Base, get_db
from app.main import create_app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    """A fresh in-memory SQLite database per test. Production uses Postgres (see README)."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, expire_on_commit=False)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def storage(tmp_path):
    return LocalStorage(str(tmp_path / "uploads"))


@pytest.fixture
def client(db_session, storage):
    app = create_app()

    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app, base_url="http://localhost", headers={"X-Requested-With": "builder"}) as c:
        yield c
