from typing import Any, Generator
from pydantic import BaseModel
from deta import Deta

from app.config import settings


# Initialize with a Project Key
deta = Deta(settings.DETA_KEY)


class DB:
    pass


def get_db() -> Generator:
    prefix: str = ""
    db: DB = DB()
    setattr(db, "users", deta.Base(f"{prefix}users"))
    setattr(db, "verifications", deta.Base(f"{prefix}verifications"))
    setattr(db, "items", deta.Base(f"{prefix}items"))
    yield db
