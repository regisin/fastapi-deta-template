from typing import Generator
from deta import Deta

import pytest

from fastapi.testclient import TestClient

from app.utils.database import get_db, DB
from app.config import settings
from app.main import app

deta = Deta(settings.DETA_KEY)

@pytest.fixture(name="db")
def db_fixture() -> Generator:
    def remove_all_records(table: _Base):
        count = None
        while not count == 0:
            fetch = table.fetch()
            count = fetch.count
            for item in fetch.items:
                table.delete(item["key"])

    try:
        prefix: str = "test_"
        db: DB = DB()
        setattr(db, "users", deta.Base(f"{prefix}users"))
        setattr(db, "verifications", deta.Base(f"{prefix}verifications"))
        setattr(db, "items", deta.Base(f"{prefix}items"))
        yield db
    finally:
        remove_all_records(db.users)
        remove_all_records(db.verifications)
        remove_all_records(db.items)


@pytest.fixture(name="client")
def client_fixture(db: DB):
    def get_db_override():
        return db
    
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()