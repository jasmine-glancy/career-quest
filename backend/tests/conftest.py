import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import models  # noqa: E402,F401  (registers all tables on Base.metadata)
from app.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.deps import get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_DB_NAME = "career_quest_test"
_base_url = settings.database_url.rsplit("/", 1)[0]
TEST_DATABASE_URL = f"{_base_url}/{TEST_DB_NAME}"
_ADMIN_DATABASE_URL = f"{_base_url}/postgres"


@pytest.fixture(scope="session")
def test_engine():
    admin_engine = create_engine(_ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    session_factory = sessionmaker(bind=test_engine)
    session = session_factory()

    yield session

    session.close()
    with test_engine.begin() as conn:
        table_names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
        conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
