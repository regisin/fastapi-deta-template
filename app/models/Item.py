from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship


class ItemBase(SQLModel):
    name: str
    description: str


class Item(ItemBase):
    key: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    key: str


class ItemUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ItemDelete(ItemBase):
    pass
